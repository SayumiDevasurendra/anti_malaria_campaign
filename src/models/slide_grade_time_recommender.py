"""
Multi-task model for slide grading + time recommendation

Architecture:
    - Shared ResNet backbone (feature extraction from images)
    - Grade classification head (I-V)
    - Time recommendation head (regression for time delta)

This model learns BOTH:
    1. What grade the slide is (classification task)
    2. How many minutes to add/subtract to reach optimal time (regression task)

Example:
    Input: Image at 6 minutes
    Output: Grade II, recommend +5.2 minutes → try 11 minutes
"""

import torch
import torch.nn as nn
import torchvision.models as models
from typing import Tuple, Optional


class SlideGradeTimeRecommender(nn.Module):
    """
    Multi-task model: Grade classification + Time recommendation

    Combines CNN image classification with regression for intelligent
    time recommendations based on visual features.
    """

    def __init__(
        self,
        architecture: str = 'resnet18',
        num_grade_classes: int = 5,
        pretrained: bool = True,
        dropout: float = 0.3,
        use_time_context: bool = True
    ):
        """
        Initialize multi-task model

        Args:
            architecture: CNN backbone ('resnet18', 'resnet50', etc.)
            num_grade_classes: Number of grade classes (default: 5 for I-V)
            pretrained: Use ImageNet pretrained weights
            dropout: Dropout rate for regularization
            use_time_context: Include current_time as input to time head
        """
        super().__init__()

        self.architecture = architecture
        self.num_grade_classes = num_grade_classes
        self.use_time_context = use_time_context

        # Shared ResNet backbone (feature extractor)
        self.backbone = self._create_backbone(architecture, pretrained)
        feature_dim = self._get_feature_dim()

        # Head 1: Grade Classification (softmax output)
        self.grade_head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(feature_dim, 256),
            nn.ReLU(),
            nn.Dropout(p=dropout),
            nn.Linear(256, num_grade_classes)
        )

        # Head 2: Time Recommendation (regression output)
        # Optionally includes current_time as additional input
        time_input_dim = feature_dim + (1 if use_time_context else 0)

        self.time_head = nn.Sequential(
            nn.Dropout(p=dropout),
            nn.Linear(time_input_dim, 128),
            nn.ReLU(),
            nn.Dropout(p=dropout / 2),  # Less dropout for regression
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, 1)  # Single continuous output (time_delta)
        )

    def _create_backbone(self, architecture: str, pretrained: bool) -> nn.Module:
        """Create CNN backbone for feature extraction"""
        arch = architecture.lower()

        if arch == 'resnet18':
            weights = models.ResNet18_Weights.DEFAULT if pretrained else None
            model = models.resnet18(weights=weights)
            # Remove final FC layer, keep up to avgpool
            model = nn.Sequential(*list(model.children())[:-1])

        elif arch == 'resnet50':
            weights = models.ResNet50_Weights.DEFAULT if pretrained else None
            model = models.resnet50(weights=weights)
            model = nn.Sequential(*list(model.children())[:-1])

        elif arch == 'efficientnet_b0':
            weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
            model = models.efficientnet_b0(weights=weights)
            model.classifier = nn.Identity()

        elif arch == 'mobilenet_v3_small':
            weights = models.MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
            model = models.mobilenet_v3_small(weights=weights)
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

    def forward(
        self,
        images: torch.Tensor,
        current_times: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass

        Args:
            images: Input images (B, C, H, W)
            current_times: Current staining times (B,) - optional

        Returns:
            grade_logits: Grade predictions (B, num_classes)
            time_deltas: Time adjustments in minutes (B, 1)
        """
        # Extract visual features using shared backbone
        features = self.backbone(images)  # (B, feature_dim, 1, 1)

        # Flatten features
        if features.dim() > 2:
            features = features.view(features.size(0), -1)  # (B, feature_dim)

        # Task 1: Grade classification
        grade_logits = self.grade_head(features)  # (B, num_classes)

        # Task 2: Time recommendation
        if self.use_time_context and current_times is not None:
            # Concatenate visual features with current time
            if current_times.dim() == 1:
                current_times = current_times.unsqueeze(1)  # (B, 1)
            time_features = torch.cat([features, current_times], dim=1)
        else:
            time_features = features

        time_deltas = self.time_head(time_features)  # (B, 1)

        return grade_logits, time_deltas

    def predict(
        self,
        images: torch.Tensor,
        current_times: Optional[torch.Tensor] = None,
        return_probs: bool = False
    ) -> dict:
        """
        High-level prediction interface

        Args:
            images: Input images (B, C, H, W)
            current_times: Current staining times (B,)
            return_probs: Return class probabilities

        Returns:
            Dictionary with predictions
        """
        self.eval()
        with torch.no_grad():
            grade_logits, time_deltas = self.forward(images, current_times)

            # Grade predictions
            grade_probs = torch.softmax(grade_logits, dim=1)
            predicted_grades = torch.argmax(grade_logits, dim=1)
            confidences = torch.max(grade_probs, dim=1)[0]

            # Time recommendations
            if current_times is not None:
                recommended_times = current_times + time_deltas.squeeze(1)
            else:
                recommended_times = None

            result = {
                'predicted_grades': predicted_grades.cpu().numpy(),
                'confidences': confidences.cpu().numpy(),
                'time_deltas': time_deltas.squeeze(1).cpu().numpy(),
            }

            if recommended_times is not None:
                result['recommended_times'] = recommended_times.cpu().numpy()

            if return_probs:
                result['grade_probabilities'] = grade_probs.cpu().numpy()

            return result


def create_grade_time_model(
    architecture: str = 'resnet18',
    num_grade_classes: int = 5,
    pretrained: bool = True,
    dropout: float = 0.3,
    use_time_context: bool = True
) -> SlideGradeTimeRecommender:
    """
    Factory function to create multi-task model

    Args:
        architecture: CNN backbone architecture
        num_grade_classes: Number of grade classes (default: 5 for I-V)
        pretrained: Use ImageNet pretrained weights
        dropout: Dropout rate
        use_time_context: Include current_time in time head

    Returns:
        Initialized model
    """
    return SlideGradeTimeRecommender(
        architecture=architecture,
        num_grade_classes=num_grade_classes,
        pretrained=pretrained,
        dropout=dropout,
        use_time_context=use_time_context
    )


if __name__ == '__main__':
    # Test model creation
    print("Creating SlideGradeTimeRecommender model...")
    model = create_grade_time_model(
        architecture='resnet18',
        num_grade_classes=5,
        pretrained=False,  # Don't download for testing
        use_time_context=True
    )

    print(f"Model created successfully!")
    print(f"Architecture: {model.architecture}")
    print(f"Parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Test forward pass
    batch_size = 4
    dummy_images = torch.randn(batch_size, 3, 512, 512)
    dummy_times = torch.tensor([6.0, 8.0, 10.0, 12.0])

    print(f"\nTesting forward pass...")
    grade_logits, time_deltas = model(dummy_images, dummy_times)

    print(f"  Input: {dummy_images.shape}, times: {dummy_times.shape}")
    print(f"  Output grade_logits: {grade_logits.shape}")
    print(f"  Output time_deltas: {time_deltas.shape}")

    # Test prediction interface
    print(f"\nTesting prediction interface...")
    predictions = model.predict(dummy_images, dummy_times, return_probs=True)

    print(f"  Predicted grades: {predictions['predicted_grades']}")
    print(f"  Confidences: {predictions['confidences']}")
    print(f"  Time deltas: {predictions['time_deltas']}")
    print(f"  Recommended times: {predictions['recommended_times']}")

    print("\n✓ Model test passed!")
