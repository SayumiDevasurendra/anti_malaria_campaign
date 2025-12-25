"""
Slide Quality Grading Model Training Script

Trains CNN models for automated Giemsa slide quality grading (AMC Grades I-V).
Supports multiple architectures, mixed precision training, and checkpoint management.

Usage:
    python train_slide_grading.py --config config/config.yaml
    python train_slide_grading.py --config config/config.yaml --resume checkpoints/checkpoints_04/checkpoint_epoch_10.pth
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from utils.stain_time_config import StainTimeConfig
from utils.stain_time_logger import setup_stain_time_logger
from utils.stain_time_seed import set_stain_time_seed
from data.stain_time_dataset import StainTimeDataset
from data.stain_time_transforms import get_stain_time_train_transforms, get_stain_time_val_transforms, StainTimeNormalization
from models.slide_grade_classifier import create_slide_grade_model
from models.slide_grade_trainer import SlideGradeTrainer


def main():
    parser = argparse.ArgumentParser(description='Train AMC Slide Quality Grading Model')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to checkpoint to resume from')
    args = parser.parse_args()

    # Load configuration
    config = StainTimeConfig(args.config)
    logger = setup_stain_time_logger(
        name='SlideGrading_Train',
        log_dir=config.get('logging.log_dir', 'logs/logs_04'),
        level=config.get('logging.level', 'INFO')
    )

    logger.info("=" * 60)
    logger.info("SLIDE QUALITY GRADING - MODEL TRAINING")
    logger.info("=" * 60)

    # Set random seed
    seed = config.get('reproducibility.seed', 42)
    deterministic = config.get('reproducibility.deterministic', True)
    set_stain_time_seed(seed, deterministic=deterministic)
    logger.info(f"Random seed set to {seed}")

    # Device
    device = config.get('hardware.device', 'cuda')
    if device == 'cuda' and not torch.cuda.is_available():
        device = 'cpu'
        logger.warning("CUDA not available, using CPU")
    logger.info(f"Using device: {device}")

    # Load data
    logger.info("\nLoading datasets...")
    processed_dir = Path(config.get('data.processed_dir', 'data/data_04/processed'))

    train_df = pd.read_csv(processed_dir / 'train.csv')
    val_df = pd.read_csv(processed_dir / 'val.csv')

    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Val samples: {len(val_df)}")

    # Stain normalization (optional)
    stain_normalizer = None
    if config.get('stain_normalization.enabled', False):
        method = config.get('stain_normalization.method', 'macenko')
        logger.info(f"Enabling stain normalization: {method}")
        stain_normalizer = StainTimeNormalization(method=method)

    # Transforms
    image_size = tuple(config.get('data.image_size', [512, 512]))
    aug_config = config.get('augmentation.train', {})

    train_transforms = get_stain_time_train_transforms(image_size, aug_config)
    val_transforms = get_stain_time_val_transforms(image_size)

    # Datasets
    train_dataset = StainTimeDataset(
        train_df,
        transform=train_transforms,
        stain_normalizer=stain_normalizer
    )

    val_dataset = StainTimeDataset(
        val_df,
        transform=val_transforms,
        stain_normalizer=stain_normalizer
    )

    # Data loaders
    batch_size = config.get('training.batch_size', 16)
    num_workers = config.get('hardware.num_workers', 4)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=config.get('hardware.pin_memory', True)
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=config.get('hardware.pin_memory', True)
    )

    logger.info(f"Batch size: {batch_size}")
    logger.info(f"Train batches: {len(train_loader)}")
    logger.info(f"Val batches: {len(val_loader)}")

    # Create model
    logger.info("\nCreating model...")
    model = create_slide_grade_model(
        model_type='single_task',
        architecture=config.get('model.architecture', 'resnet18'),
        num_grade_classes=config.get('model.num_grade_classes', 5),
        pretrained=config.get('model.pretrained', True),
        dropout=config.get('model.dropout', 0.3)
    )

    logger.info(f"Architecture: {config.get('model.architecture', 'resnet18')}")
    logger.info(f"Pretrained: {config.get('model.pretrained', True)}")

    # Loss function
    criterion = nn.CrossEntropyLoss()

    # Optimizer
    lr = config.get('training.learning_rate', 0.001)
    weight_decay = config.get('training.weight_decay', 0.0001)
    optimizer_name = config.get('training.optimizer', 'adam').lower()

    if optimizer_name == 'adam':
        optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == 'adamw':
        optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    elif optimizer_name == 'sgd':
        optimizer = optim.SGD(model.parameters(), lr=lr, weight_decay=weight_decay, momentum=0.9)
    else:
        raise ValueError(f"Unknown optimizer: {optimizer_name}")

    logger.info(f"Optimizer: {optimizer_name}")
    logger.info(f"Learning rate: {lr}")

    # Scheduler
    scheduler_type = config.get('training.scheduler.type', 'cosine').lower()
    if scheduler_type == 'cosine':
        scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=config.get('training.num_epochs', 50)
        )
    elif scheduler_type == 'step':
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1)
    elif scheduler_type == 'plateau':
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', patience=5)
    else:
        scheduler = None

    if scheduler:
        logger.info(f"Scheduler: {scheduler_type}")

    # Trainer
    trainer = SlideGradeTrainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        criterion=criterion,
        optimizer=optimizer,
        scheduler=scheduler,
        device=device,
        use_amp=config.get('training.use_amp', True),
        save_dir=config.get('model.checkpoint_dir', 'checkpoints/checkpoints_04'),
        logger=logger.info
    )

    # Resume from checkpoint
    if args.resume:
        logger.info(f"\nResuming from checkpoint: {args.resume}")
        trainer.load_checkpoint(args.resume)

    # Train
    logger.info("\nStarting training...")
    logger.info("-" * 60)

    num_epochs = config.get('training.num_epochs', 50)
    early_stopping_patience = config.get('training.early_stopping.patience', 10)
    save_frequency = config.get('training.save_frequency', 5)

    trainer.fit(
        num_epochs=num_epochs,
        early_stopping_patience=early_stopping_patience,
        save_frequency=save_frequency
    )

    logger.info("\n" + "=" * 60)
    logger.info("TRAINING COMPLETE!")
    logger.info(f"Best validation accuracy: {trainer.best_val_acc:.2f}%")
    logger.info(f"Best model saved to: {trainer.save_dir / 'best_model.pth'}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
