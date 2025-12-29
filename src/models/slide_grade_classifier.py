"""
Slide Grade Classifier Module

CNN architectures for automated Giemsa slide grading (AMC Grades I-V).
Supports multiple backbone architectures and multi-task learning.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Optional, Tuple


class SlideGradeClassifier(nn.Module):
    """CNN classifier for AMC slide quality grading (I-V)"""

    def __init__(
        self,
        architecture: str = 'resnet18',
        num_classes: int = 5,
        pretrained: bool = True,
        dropout: float = 0.3
    ):
        """
        Initialize grade classifier

        Args:
            architecture: Backbone architecture (resnet18, resnet50, efficientnet_b0, mobilenet_v3_small)
            num_classes: Number of grade classes (5 for I-V)
            pretrained: Use ImageNet pretrained weights
            dropout: Dropout probability
        """
        super().__init__()

        self.architecture = architecture
        self.num_classes = num_classes

        # Create backbone
        self.backbone = self._create_backbone(architecture, pretrained)

        # Get feature dimension
        feature_dim = self._get_feature_dim()

        # Classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_classes)
        )

    def _create_backbone(self, architecture: str, pretrained: bool):
        """Create CNN backbone"""
        arch = architecture.lower()

        if arch == 'resnet18':
            model = models.resnet18(pretrained=pretrained)
            # Remove final FC layer
            model = nn.Sequential(*list(model.children())[:-1])

        elif arch == 'resnet50':
            model = models.resnet50(pretrained=pretrained)
            model = nn.Sequential(*list(model.children())[:-1])

        elif arch == 'efficientnet_b0':
            model = models.efficientnet_b0(pretrained=pretrained)
            model.classifier = nn.Identity()

        elif arch == 'mobilenet_v3_small':
            model = models.mobilenet_v3_small(pretrained=pretrained)
            model.classifier = nn.Identity()

        else:
            raise ValueError(f"Unknown architecture: {architecture}")

        return model

    def _get_feature_dim(self) -> int:
        """Get feature dimension from backbone"""
        arch = self.architecture.lower()

        feature_dims = {
            'resnet18': 512,
            'resnet50': 2048,
            'efficientnet_b0': 1280,
            'mobilenet_v3_small': 576
        }

        return feature_dims[arch]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass

        Args:
            x: Input images (B, C, H, W)

        Returns:
            Logits (B, num_classes)
        """
        # Extract features
        features = self.backbone(x)

        # Flatten if needed
        if features.dim() > 2:
            features = features.view(features.size(0), -1)

        # Classify
        logits = self.classifier(features)

        return logits


class SlideGradeMultiTaskModel(nn.Module):
    """Multi-task model for grade classification + failure reason prediction"""

    def __init__(
        self,
        architecture: str = 'resnet18',
        num_grade_classes: int = 5,
        num_reason_classes: int = 6,
        pretrained: bool = True,
        dropout: float = 0.3
    ):
        """
        Initialize multi-task model

        Args:
            architecture: Backbone architecture
            num_grade_classes: Number of grade classes (5 for I-V)
            num_reason_classes: Number of failure reasons (multi-label)
            pretrained: Use ImageNet pretrained weights
            dropout: Dropout probability
        """
        super().__init__()

        self.architecture = architecture

        # Shared backbone
        self.backbone = self._create_backbone(architecture, pretrained)
        feature_dim = self._get_feature_dim()

        # Grade classification head
        self.grade_head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_grade_classes)
        )

        # Failure reason prediction head (multi-label)
        self.reason_head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_reason_classes)
        )

    def _create_backbone(self, architecture: str, pretrained: bool):
        """Create CNN backbone (same as SlideGradeClassifier)"""
        arch = architecture.lower()

        if arch == 'resnet18':
            model = models.resnet18(pretrained=pretrained)
            model = nn.Sequential(*list(model.children())[:-1])
        elif arch == 'resnet50':
            model = models.resnet50(pretrained=pretrained)
            model = nn.Sequential(*list(model.children())[:-1])
        elif arch == 'efficientnet_b0':
            model = models.efficientnet_b0(pretrained=pretrained)
            model.classifier = nn.Identity()
        elif arch == 'mobilenet_v3_small':
            model = models.mobilenet_v3_small(pretrained=pretrained)
            model.classifier = nn.Identity()
        else:
            raise ValueError(f"Unknown architecture: {architecture}")

        return model

    def _get_feature_dim(self) -> int:
        """Get feature dimension from backbone"""
        feature_dims = {
            'resnet18': 512,
            'resnet50': 2048,
            'efficientnet_b0': 1280,
            'mobilenet_v3_small': 576
        }
        return feature_dims[self.architecture.lower()]

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass

        Args:
            x: Input images (B, C, H, W)

        Returns:
            Tuple of (grade_logits, reason_logits)
        """
        # Extract features
        features = self.backbone(x)

        # Flatten
        if features.dim() > 2:
            features = features.view(features.size(0), -1)

        # Predictions
        grade_logits = self.grade_head(features)
        reason_logits = self.reason_head(features)

        return grade_logits, reason_logits


def create_slide_grade_model(
    model_type: str = 'single_task',
    architecture: str = 'resnet18',
    num_grade_classes: int = 5,
    num_reason_classes: int = 6,
    pretrained: bool = True,
    dropout: float = 0.3
) -> nn.Module:
    """
    Factory function to create models

    Args:
        model_type: 'single_task' or 'multi_task'
        architecture: CNN architecture
        num_grade_classes: Number of grade classes
        num_reason_classes: Number of failure reason classes
        pretrained: Use pretrained weights
        dropout: Dropout probability

    Returns:
        Model instance
    """
    if model_type == 'single_task':
        return SlideGradeClassifier(
            architecture=architecture,
            num_classes=num_grade_classes,
            pretrained=pretrained,
            dropout=dropout
        )
    elif model_type == 'multi_task':
        return SlideGradeMultiTaskModel(
            architecture=architecture,
            num_grade_classes=num_grade_classes,
            num_reason_classes=num_reason_classes,
            pretrained=pretrained,
            dropout=dropout
        )
    else:
        raise ValueError(f"Unknown model_type: {model_type}")
