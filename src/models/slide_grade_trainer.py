"""
Slide Grade Training Pipeline Module

Training manager with support for mixed precision, learning rate scheduling,
checkpointing, and early stopping.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from typing import Optional, Dict, Callable
from tqdm import tqdm
import numpy as np
from pathlib import Path


class SlideGradeTrainer:
    """Training manager for slide grading models"""

    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        criterion: nn.Module,
        optimizer: optim.Optimizer,
        scheduler: Optional[optim.lr_scheduler._LRScheduler] = None,
        device: str = 'cuda',
        use_amp: bool = True,
        save_dir: str = 'checkpoints/checkpoints_04',
        logger: Optional[Callable] = None
    ):
        """
        Initialize trainer

        Args:
            model: PyTorch model
            train_loader: Training data loader
            val_loader: Validation data loader
            criterion: Loss function
            optimizer: Optimizer
            scheduler: Learning rate scheduler
            device: Device ('cuda' or 'cpu')
            use_amp: Use automatic mixed precision
            save_dir: Directory to save checkpoints
            logger: Logger function
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.device = device
        self.use_amp = use_amp and device == 'cuda'
        self.save_dir = Path(save_dir)
        self.logger = logger or print

        # Create save directory
        self.save_dir.mkdir(parents=True, exist_ok=True)

        # Mixed precision scaler
        self.scaler = GradScaler() if self.use_amp else None

        # Training state
        self.epoch = 0
        self.best_val_loss = float('inf')
        self.best_val_acc = 0.0
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': []
        }

    def train_epoch(self) -> Dict[str, float]:
        """Train for one epoch"""
        self.model.train()
        running_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(self.train_loader, desc=f'Epoch {self.epoch + 1} [Train]')

        for batch_idx, batch in enumerate(pbar):
            # Unpack batch
            if len(batch) == 2:
                images, labels = batch
            else:
                images, labels = batch[0], batch[1]

            images = images.to(self.device)
            labels = labels.to(self.device)

            # Zero gradients
            self.optimizer.zero_grad()

            # Forward pass with AMP
            if self.use_amp:
                with autocast():
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)

                # Backward pass
                self.scaler.scale(loss).backward()
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()

            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })

        epoch_loss = running_loss / len(self.train_loader)
        epoch_acc = 100. * correct / total

        return {'loss': epoch_loss, 'acc': epoch_acc}

    @torch.no_grad()
    def validate(self) -> Dict[str, float]:
        """Validate model"""
        self.model.eval()
        running_loss = 0.0
        correct = 0
        total = 0

        pbar = tqdm(self.val_loader, desc=f'Epoch {self.epoch + 1} [Val]')

        for batch_idx, batch in enumerate(pbar):
            # Unpack batch
            if len(batch) == 2:
                images, labels = batch
            else:
                images, labels = batch[0], batch[1]

            images = images.to(self.device)
            labels = labels.to(self.device)

            # Forward pass
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)

            # Statistics
            running_loss += loss.item()
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()

            # Update progress bar
            pbar.set_postfix({
                'loss': running_loss / (batch_idx + 1),
                'acc': 100. * correct / total
            })

        epoch_loss = running_loss / len(self.val_loader)
        epoch_acc = 100. * correct / total

        return {'loss': epoch_loss, 'acc': epoch_acc}

    def save_checkpoint(self, filename: str, is_best: bool = False):
        """Save model checkpoint"""
        checkpoint = {
            'epoch': self.epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_val_loss': self.best_val_loss,
            'best_val_acc': self.best_val_acc,
            'history': self.history
        }

        if self.scheduler is not None:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()

        # Save checkpoint
        checkpoint_path = self.save_dir / filename
        torch.save(checkpoint, checkpoint_path)

        # Save as best if needed
        if is_best:
            best_path = self.save_dir / 'best_model.pth'
            torch.save(checkpoint, best_path)

    def load_checkpoint(self, filename: str):
        """Load model checkpoint"""
        checkpoint_path = self.save_dir / filename

        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

        checkpoint = torch.load(checkpoint_path, map_location=self.device)

        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epoch = checkpoint['epoch']
        self.best_val_loss = checkpoint['best_val_loss']
        self.best_val_acc = checkpoint['best_val_acc']
        self.history = checkpoint['history']

        if self.scheduler is not None and 'scheduler_state_dict' in checkpoint:
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])

        self.logger(f"Loaded checkpoint from epoch {self.epoch}")

    def fit(
        self,
        num_epochs: int,
        early_stopping_patience: Optional[int] = None,
        save_frequency: int = 5
    ):
        """
        Train model for multiple epochs

        Args:
            num_epochs: Number of epochs to train
            early_stopping_patience: Stop if no improvement for N epochs
            save_frequency: Save checkpoint every N epochs
        """
        patience_counter = 0

        for epoch in range(num_epochs):
            self.epoch = epoch

            # Train
            train_metrics = self.train_epoch()
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['train_acc'].append(train_metrics['acc'])

            # Validate
            val_metrics = self.validate()
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_acc'].append(val_metrics['acc'])

            # Log
            self.logger(
                f"Epoch {epoch + 1}/{num_epochs} - "
                f"Train Loss: {train_metrics['loss']:.4f}, "
                f"Train Acc: {train_metrics['acc']:.2f}% - "
                f"Val Loss: {val_metrics['loss']:.4f}, "
                f"Val Acc: {val_metrics['acc']:.2f}%"
            )

            # Learning rate scheduler
            if self.scheduler is not None:
                if isinstance(self.scheduler, optim.lr_scheduler.ReduceLROnPlateau):
                    self.scheduler.step(val_metrics['loss'])
                else:
                    self.scheduler.step()

            # Check if best model
            is_best = val_metrics['acc'] > self.best_val_acc

            if is_best:
                self.best_val_acc = val_metrics['acc']
                self.best_val_loss = val_metrics['loss']
                patience_counter = 0
                self.logger(f"✓ New best model! Val Acc: {self.best_val_acc:.2f}%")
            else:
                patience_counter += 1

            # Save checkpoint
            if (epoch + 1) % save_frequency == 0 or is_best:
                self.save_checkpoint(f'checkpoint_epoch_{epoch + 1}.pth', is_best=is_best)

            # Early stopping
            if early_stopping_patience and patience_counter >= early_stopping_patience:
                self.logger(f"Early stopping triggered after {epoch + 1} epochs")
                break

        self.logger(f"\nTraining complete! Best Val Acc: {self.best_val_acc:.2f}%")
