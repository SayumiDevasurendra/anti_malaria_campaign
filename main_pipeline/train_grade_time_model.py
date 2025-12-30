"""
Training script for multi-task model: Grade classification + Time recommendation

Trains SlideGradeTimeRecommender with combined loss:
    - Classification loss (CrossEntropy) for grade prediction
    - Regression loss (MSE/Huber) for time delta prediction
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from pathlib import Path
import sys
import argparse
from tqdm import tqdm
import numpy as np
import pandas as pd
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.slide_grade_time_recommender import create_grade_time_model
from src.data.stain_time_optimal_dataset import StainTimeOptimalDataset, collate_fn
from src.data.stain_time_transforms import (
    get_stain_time_train_transforms,
    get_stain_time_val_transforms
)
from src.utils.class_balance_utils import (
    calculate_class_weights,
    create_joint_weighted_sampler
)


class MultiTaskLoss(nn.Module):
    """
    Combined loss for multi-task learning

    L_total = α * L_grade + β * L_time

    where:
        L_grade = Weighted CrossEntropyLoss (classification with class balancing)
        L_time = Huber Loss (robust regression)
    """

    def __init__(
        self,
        grade_weight: float = 0.7,
        time_weight: float = 0.3,
        huber_delta: float = 2.0,
        class_weights: torch.Tensor = None
    ):
        """
        Args:
            grade_weight: Weight for classification loss (α)
            time_weight: Weight for regression loss (β)
            huber_delta: Delta parameter for Huber loss (less sensitive to outliers)
            class_weights: Tensor of class weights for imbalanced grades (shape: [num_classes])
        """
        super().__init__()
        self.grade_weight = grade_weight
        self.time_weight = time_weight

        # Use weighted CrossEntropyLoss if class weights provided
        self.grade_criterion = nn.CrossEntropyLoss(weight=class_weights)
        self.time_criterion = nn.HuberLoss(delta=huber_delta)

    def forward(
        self,
        grade_logits: torch.Tensor,
        time_deltas_pred: torch.Tensor,
        grade_targets: torch.Tensor,
        time_deltas_target: torch.Tensor
    ):
        """
        Compute combined loss

        Returns:
            total_loss, grade_loss, time_loss
        """
        grade_loss = self.grade_criterion(grade_logits, grade_targets)
        time_loss = self.time_criterion(time_deltas_pred.squeeze(), time_deltas_target)

        total_loss = self.grade_weight * grade_loss + self.time_weight * time_loss

        return total_loss, grade_loss, time_loss


def train_epoch(model, dataloader, criterion, optimizer, device, epoch):
    """Train for one epoch"""
    model.train()

    total_loss = 0
    total_grade_loss = 0
    total_time_loss = 0
    correct_grades = 0
    total_samples = 0

    pbar = tqdm(dataloader, desc=f"Epoch {epoch} [Train]")

    for batch in pbar:
        images, grades, current_times, time_deltas = batch[:4]

        images = images.to(device)
        grades = grades.to(device)
        current_times = current_times.to(device)
        time_deltas = time_deltas.to(device)

        # Forward pass
        optimizer.zero_grad()
        grade_logits, time_deltas_pred = model(images, current_times)

        # Compute loss
        loss, grade_loss, time_loss = criterion(
            grade_logits, time_deltas_pred, grades, time_deltas
        )

        # Backward pass
        loss.backward()
        optimizer.step()

        # Track metrics
        total_loss += loss.item() * len(images)
        total_grade_loss += grade_loss.item() * len(images)
        total_time_loss += time_loss.item() * len(images)

        pred_grades = torch.argmax(grade_logits, dim=1)
        correct_grades += (pred_grades == grades).sum().item()
        total_samples += len(images)

        # Update progress bar
        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'grade_acc': f'{correct_grades/total_samples:.3f}',
            'time_mae': f'{torch.abs(time_deltas_pred.squeeze() - time_deltas).mean().item():.2f}'
        })

    # Epoch statistics
    avg_loss = total_loss / total_samples
    avg_grade_loss = total_grade_loss / total_samples
    avg_time_loss = total_time_loss / total_samples
    grade_acc = correct_grades / total_samples

    return {
        'loss': avg_loss,
        'grade_loss': avg_grade_loss,
        'time_loss': avg_time_loss,
        'grade_accuracy': grade_acc
    }


@torch.no_grad()
def validate_epoch(model, dataloader, criterion, device, epoch):
    """Validate for one epoch"""
    model.eval()

    total_loss = 0
    total_grade_loss = 0
    total_time_loss = 0
    correct_grades = 0
    total_samples = 0

    time_errors = []

    pbar = tqdm(dataloader, desc=f"Epoch {epoch} [Val]")

    for batch in pbar:
        images, grades, current_times, time_deltas = batch[:4]

        images = images.to(device)
        grades = grades.to(device)
        current_times = current_times.to(device)
        time_deltas = time_deltas.to(device)

        # Forward pass
        grade_logits, time_deltas_pred = model(images, current_times)

        # Compute loss
        loss, grade_loss, time_loss = criterion(
            grade_logits, time_deltas_pred, grades, time_deltas
        )

        # Track metrics
        total_loss += loss.item() * len(images)
        total_grade_loss += grade_loss.item() * len(images)
        total_time_loss += time_loss.item() * len(images)

        pred_grades = torch.argmax(grade_logits, dim=1)
        correct_grades += (pred_grades == grades).sum().item()
        total_samples += len(images)

        # Track time errors
        errors = torch.abs(time_deltas_pred.squeeze() - time_deltas).cpu().numpy()
        time_errors.extend(errors.tolist())

        pbar.set_postfix({
            'loss': f'{loss.item():.4f}',
            'grade_acc': f'{correct_grades/total_samples:.3f}'
        })

    # Epoch statistics
    avg_loss = total_loss / total_samples
    avg_grade_loss = total_grade_loss / total_samples
    avg_time_loss = total_time_loss / total_samples
    grade_acc = correct_grades / total_samples
    time_mae = np.mean(time_errors)

    return {
        'loss': avg_loss,
        'grade_loss': avg_grade_loss,
        'time_loss': avg_time_loss,
        'grade_accuracy': grade_acc,
        'time_mae': time_mae
    }


def train_model(
    train_csv: str,
    val_csv: str,
    checkpoint_dir: str = 'checkpoints_grade_time',
    architecture: str = 'resnet18',
    img_size: tuple = (512, 512),
    batch_size: int = 16,
    num_epochs: int = 50,
    lr: float = 1e-4,
    grade_weight: float = 0.7,
    time_weight: float = 0.3,
    use_class_weights: bool = True,
    use_joint_sampler: bool = True,
    device: str = 'cuda',
    seed: int = 42
):
    """
    Main training function with enhanced class balancing

    Args:
        train_csv: Path to training CSV (train_optimal.csv)
        val_csv: Path to validation CSV (val_optimal.csv)
        checkpoint_dir: Directory to save checkpoints
        architecture: CNN backbone architecture
        img_size: Input image size
        batch_size: Batch size for training
        num_epochs: Number of training epochs
        lr: Learning rate
        grade_weight: Weight for grade loss
        time_weight: Weight for time loss
        use_class_weights: Use class weights in loss function
        use_joint_sampler: Use joint weighted sampler (grade + dilution + time_delta)
        device: Device to train on
        seed: Random seed
    """
    # Set random seeds
    torch.manual_seed(seed)
    np.random.seed(seed)

    # Create checkpoint directory
    checkpoint_dir = Path(checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    print(f"{'='*60}")
    print(f"Training Multi-Task Model: Grade + Time Recommendation")
    print(f"{'='*60}")
    print(f"Architecture: {architecture}")
    print(f"Image size: {img_size}")
    print(f"Batch size: {batch_size}")
    print(f"Learning rate: {lr}")
    print(f"Loss weights: {grade_weight:.2f} (grade) + {time_weight:.2f} (time)")
    print(f"Device: {device}")
    print(f"{'='*60}\n")

    # Create datasets
    print("Loading datasets...")
    train_transform = get_stain_time_train_transforms(img_size=img_size)
    val_transform = get_stain_time_val_transforms(img_size=img_size)

    train_dataset = StainTimeOptimalDataset(
        csv_path=train_csv,
        transform=train_transform,
        return_metadata=False
    )

    val_dataset = StainTimeOptimalDataset(
        csv_path=val_csv,
        transform=val_transform,
        return_metadata=False
    )

    print(f"  Train: {len(train_dataset)} images")
    print(f"  Val: {len(val_dataset)} images\n")

    # Class balancing setup
    print("Setting up class balancing...")

    # 1. Calculate class weights for loss function
    if use_class_weights:
        train_labels = train_dataset.df['grade_numeric'].values - 1  # Convert to 0-indexed
        class_weights_tensor = calculate_class_weights(train_labels, num_classes=5, method='inverse')
        class_weights_tensor = class_weights_tensor.to(device)
        print(f"  ✓ Class weights calculated:")
        for i in range(5):
            if class_weights_tensor[i] > 0:
                print(f"      Grade {i+1}: {class_weights_tensor[i]:.4f}")
    else:
        class_weights_tensor = None
        print(f"  ✗ Class weights disabled")

    # 2. Create sampler
    if use_joint_sampler:
        print(f"  ✓ Using joint weighted sampler (grade + dilution + time_delta)")
        weighted_sampler = create_joint_weighted_sampler(
            df=train_dataset.df,
            grade_weight=0.5,
            dilution_weight=0.3,
            time_delta_weight=0.2,
            method='inverse'
        )
    else:
        print(f"  ✓ Using simple grade-based weighted sampler")
        from torch.utils.data import WeightedRandomSampler
        sample_weights = train_dataset.get_sample_weights()
        weighted_sampler = WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True
        )

    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=weighted_sampler,  # Use weighted sampler instead of shuffle
        num_workers=4,
        collate_fn=collate_fn,
        pin_memory=True if device == 'cuda' else False
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        collate_fn=collate_fn,
        pin_memory=True if device == 'cuda' else False
    )

    # Create model
    print("Creating model...")
    model = create_grade_time_model(
        architecture=architecture,
        num_grade_classes=5,
        pretrained=True,
        use_time_context=True
    )
    model = model.to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}\n")

    # Create loss and optimizer
    criterion = MultiTaskLoss(
        grade_weight=grade_weight,
        time_weight=time_weight,
        huber_delta=2.0,
        class_weights=class_weights_tensor  # Pass class weights to loss
    )

    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )

    # Training loop
    best_val_loss = float('inf')
    history = []

    for epoch in range(1, num_epochs + 1):
        print(f"\nEpoch {epoch}/{num_epochs}")
        print(f"{'-'*60}")

        # Train
        train_metrics = train_epoch(model, train_loader, criterion, optimizer, device, epoch)

        # Validate
        val_metrics = validate_epoch(model, val_loader, criterion, device, epoch)

        # Scheduler step
        scheduler.step(val_metrics['loss'])

        # Print epoch summary
        print(f"\nEpoch {epoch} Summary:")
        print(f"  Train Loss: {train_metrics['loss']:.4f} | Grade Acc: {train_metrics['grade_accuracy']:.3f}")
        print(f"  Val Loss: {val_metrics['loss']:.4f} | Grade Acc: {val_metrics['grade_accuracy']:.3f} | Time MAE: {val_metrics['time_mae']:.2f} min")

        # Save history
        history.append({
            'epoch': epoch,
            'train_loss': train_metrics['loss'],
            'train_grade_acc': train_metrics['grade_accuracy'],
            'val_loss': val_metrics['loss'],
            'val_grade_acc': val_metrics['grade_accuracy'],
            'val_time_mae': val_metrics['time_mae']
        })

        # Save best model
        if val_metrics['loss'] < best_val_loss:
            best_val_loss = val_metrics['loss']
            checkpoint_path = checkpoint_dir / 'best_model.pth'
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_metrics['loss'],
                'val_grade_acc': val_metrics['grade_accuracy'],
                'val_time_mae': val_metrics['time_mae'],
                'architecture': architecture,
                'img_size': img_size
            }, checkpoint_path)
            print(f"  ✓ Saved best model (val_loss: {val_metrics['loss']:.4f})")

        # Save checkpoint every 10 epochs
        if epoch % 10 == 0:
            checkpoint_path = checkpoint_dir / f'checkpoint_epoch_{epoch}.pth'
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
            }, checkpoint_path)

    # Save training history
    history_df = pd.DataFrame(history)
    history_df.to_csv(checkpoint_dir / 'training_history.csv', index=False)

    print(f"\n{'='*60}")
    print(f"Training complete!")
    print(f"Best validation loss: {best_val_loss:.4f}")
    print(f"Checkpoints saved to: {checkpoint_dir}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(description="Train multi-task grade + time model with class balancing")
    parser.add_argument('--train-csv', type=str, required=True, help='Path to training CSV (train_optimal.csv)')
    parser.add_argument('--val-csv', type=str, required=True, help='Path to validation CSV (val_optimal.csv)')
    parser.add_argument('--checkpoint-dir', type=str, default='checkpoints_grade_time', help='Checkpoint directory')
    parser.add_argument('--architecture', type=str, default='resnet18', choices=['resnet18', 'resnet50', 'efficientnet_b0'])
    parser.add_argument('--img-size', type=int, default=512, help='Input image size')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size')
    parser.add_argument('--epochs', type=int, default=50, help='Number of epochs')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--grade-weight', type=float, default=0.7, help='Weight for grade loss')
    parser.add_argument('--time-weight', type=float, default=0.3, help='Weight for time loss')
    parser.add_argument('--no-class-weights', action='store_true', help='Disable class weights in loss')
    parser.add_argument('--no-joint-sampler', action='store_true', help='Use simple grade sampler instead of joint')
    parser.add_argument('--device', type=str, default='cuda', choices=['cuda', 'cpu'])
    parser.add_argument('--seed', type=int, default=42, help='Random seed')

    args = parser.parse_args()

    train_model(
        train_csv=args.train_csv,
        val_csv=args.val_csv,
        checkpoint_dir=args.checkpoint_dir,
        architecture=args.architecture,
        img_size=(args.img_size, args.img_size),
        batch_size=args.batch_size,
        num_epochs=args.epochs,
        lr=args.lr,
        grade_weight=args.grade_weight,
        time_weight=args.time_weight,
        use_class_weights=not args.no_class_weights,
        use_joint_sampler=not args.no_joint_sampler,
        device=args.device,
        seed=args.seed
    )


if __name__ == '__main__':
    main()
