"""
Slide Quality Grading Model Training Script (WITH CLASS BALANCING)

Enhanced training script with hybrid approach to handle class imbalance:
1. Class weights in loss function
2. Weighted random sampling for balanced batches
3. Targeted augmentation for minority classes

Usage:
    python train_slide_grading_balanced.py --config config/config.yaml
    python train_slide_grading_balanced.py --config config/config.yaml --resume checkpoints/checkpoint.pth
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
from utils.stain_time_balance_utils import (
    calculate_class_weights,
    create_weighted_sampler,
    analyze_class_distribution,
    print_class_distribution
)
from data.stain_time_balanced_dataset import BalancedStainTimeDataset
from data.stain_time_dataset import StainTimeDataset
from data.stain_time_transforms import (
    get_stain_time_train_transforms,
    get_stain_time_val_transforms,
    get_aggressive_augmentation_transforms,
    StainTimeNormalization
)
from models.slide_grade_classifier import create_slide_grade_model
from models.slide_grade_trainer import SlideGradeTrainer


def main():
    parser = argparse.ArgumentParser(description='Train AMC Slide Quality Grading Model (Balanced)')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--resume', type=str, default=None,
                        help='Path to checkpoint to resume from')
    parser.add_argument('--balance-method', type=str, default='hybrid',
                        choices=['weights', 'sampling', 'augmentation', 'hybrid'],
                        help='Class balancing method to use')
    args = parser.parse_args()

    # Load configuration
    config = StainTimeConfig(args.config)
    logger = setup_stain_time_logger(
        name='SlideGrading_Balanced_Train',
        log_dir=config.get('logging.log_dir', 'logs/logs_04'),
        level=config.get('logging.level', 'INFO')
    )

    logger.info("=" * 60)
    logger.info("SLIDE QUALITY GRADING - BALANCED MODEL TRAINING")
    logger.info("=" * 60)
    logger.info(f"Balance method: {args.balance_method}")

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
    splits_dir = Path(config.get('data.splits_dir', 'data/data_04/splits'))

    train_df = pd.read_csv(splits_dir / 'train.csv')
    val_df = pd.read_csv(splits_dir / 'val.csv')

    logger.info(f"Train samples: {len(train_df)}")
    logger.info(f"Val samples: {len(val_df)}")

    # Analyze class distribution
    train_stats = analyze_class_distribution(train_df)
    print_class_distribution(train_stats, "Training Set Class Distribution (Before Balancing)")

    # Calculate class weights
    logger.info("\nCalculating class weights...")
    train_labels = train_df['grade_numeric'].values - 1  # Convert to 0-indexed
    class_weights = calculate_class_weights(train_labels, num_classes=5, method='inverse')

    logger.info("Class weights (for loss function):")
    for i, weight in enumerate(class_weights):
        grade_num = i + 1
        logger.info(f"  Grade {grade_num} (index {i}): {weight:.4f}")

    # Stain normalization (optional)
    stain_normalizer = None
    if config.get('stain_normalization.enabled', False):
        method = config.get('stain_normalization.method', 'macenko')
        logger.info(f"Enabling stain normalization: {method}")
        stain_normalizer = StainTimeNormalization(method=method)

    # Transforms
    image_size = tuple(config.get('data.image_size', [512, 512]))
    aug_config = config.get('augmentation.train', {})

    # Base transform (standard augmentation for all)
    base_transform = get_stain_time_train_transforms(image_size, aug_config)

    # Stronger transform for minority classes
    minority_transform = get_aggressive_augmentation_transforms(image_size, aug_config)

    # Validation transform (no augmentation)
    val_transform = get_stain_time_val_transforms(image_size)

    # Create datasets based on balance method
    logger.info(f"\nCreating datasets with balance method: {args.balance_method}")

    if args.balance_method in ['augmentation', 'hybrid']:
        # Use targeted augmentation
        train_dataset = BalancedStainTimeDataset(
            train_df,
            base_transform=base_transform,
            minority_transform=minority_transform,
            stain_normalizer=stain_normalizer,
            minority_classes=None  # Auto-detect
        )
    else:
        # Use standard dataset
        train_dataset = StainTimeDataset(
            train_df,
            transform=base_transform,
            stain_normalizer=stain_normalizer
        )

    val_dataset = StainTimeDataset(
        val_df,
        transform=val_transform,
        stain_normalizer=stain_normalizer
    )

    # Create data loaders with weighted sampling if specified
    batch_size = config.get('training.batch_size', 16)
    num_workers = config.get('hardware.num_workers', 4)
    pin_memory = config.get('hardware.pin_memory', True)

    if args.balance_method in ['sampling', 'hybrid']:
        # Use weighted sampler
        logger.info("Creating weighted random sampler for balanced batches...")
        train_sampler = create_weighted_sampler(train_labels, num_classes=5)

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            sampler=train_sampler,  # Use sampler instead of shuffle
            num_workers=num_workers,
            pin_memory=pin_memory
        )
    else:
        # Standard random shuffling
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory
        )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory
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

    # Loss function with class weights if specified
    if args.balance_method in ['weights', 'hybrid']:
        logger.info("Using weighted CrossEntropyLoss")
        criterion = nn.CrossEntropyLoss(weight=class_weights.to(device))
    else:
        logger.info("Using standard CrossEntropyLoss")
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
        save_dir=config.get('model.checkpoint_dir', 'checkpoints/checkpoints_04_balanced'),
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
