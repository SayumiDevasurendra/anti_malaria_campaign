"""Image transforms and augmentation for Giemsa-stained slides"""

import torch
import torchvision.transforms as T
from typing import Tuple, Optional
import numpy as np
import cv2


class GiemseStainAugmentation:
    """Conservative augmentation for Giemsa-stained slides"""

    def __init__(
        self,
        brightness: float = 0.1,
        contrast: float = 0.1,
        saturation: float = 0.05,
        hue: float = 0.02
    ):
        """Init conservative color jitter for medical images"""
        self.color_jitter = T.ColorJitter(
            brightness=brightness,
            contrast=contrast,
            saturation=saturation,
            hue=hue
        )

    def __call__(self, image):
        return self.color_jitter(image)


def get_stain_time_train_transforms(image_size: Tuple[int, int] = (512, 512), config: Optional[dict] = None):
    """Get training transforms: rotation, flips, color jitter, blur"""
    if config is None:
        config = {
            'random_rotation': 15,
            'random_horizontal_flip': 0.5,
            'random_vertical_flip': 0.5,
            'brightness_jitter': 0.1,
            'contrast_jitter': 0.1,
            'saturation_jitter': 0.05,
            'hue_jitter': 0.02,
            'gaussian_blur_prob': 0.1,
        }

    transforms_list = [
        T.Resize(image_size),
        T.RandomRotation(degrees=config.get('random_rotation', 15)),
    ]

    # Horizontal flip
    if config.get('random_horizontal_flip', 0) > 0:
        transforms_list.append(T.RandomHorizontalFlip(p=config['random_horizontal_flip']))

    # Vertical flip
    if config.get('random_vertical_flip', 0) > 0:
        transforms_list.append(T.RandomVerticalFlip(p=config['random_vertical_flip']))

    # Conservative color jittering
    transforms_list.append(
        GiemseStainAugmentation(
            brightness=config.get('brightness_jitter', 0.1),
            contrast=config.get('contrast_jitter', 0.1),
            saturation=config.get('saturation_jitter', 0.05),
            hue=config.get('hue_jitter', 0.02)
        )
    )

    # Gaussian blur (low probability)
    if config.get('gaussian_blur_prob', 0) > 0:
        transforms_list.append(T.RandomApply([T.GaussianBlur(kernel_size=3)], p=config['gaussian_blur_prob']))

    # Convert to tensor and normalize
    transforms_list.extend([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])  # ImageNet stats
    ])

    return T.Compose(transforms_list)


def get_stain_time_val_transforms(image_size: Tuple[int, int] = (512, 512)):
    """Get validation transforms: resize + normalize only (no augmentation)"""
    return T.Compose([
        T.Resize(image_size),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


class StainTimeNormalization:
    """Stain normalization for Giemsa-stained slides"""

    def __init__(self, method: str = 'macenko', reference_image: Optional[np.ndarray] = None):
        """Init stain normalizer: 'macenko', 'reinhard', or 'none'"""
        self.method = method.lower()
        self.reference_image = reference_image

        if self.method != 'none':
            try:
                import staintools
                self.normalizer = self._get_normalizer()
            except ImportError:
                print("Warning: staintools not installed. Skipping stain normalization.")
                self.method = 'none'

    def _get_normalizer(self):
        """Get stain normalizer based on method"""
        import staintools

        if self.method == 'macenko':
            normalizer = staintools.StainNormalizer(method='macenko')
        elif self.method == 'reinhard':
            normalizer = staintools.StainNormalizer(method='reinhard')
        else:
            return None

        # Fit to reference image if provided
        if self.reference_image is not None:
            normalizer.fit(self.reference_image)

        return normalizer

    def __call__(self, image: np.ndarray) -> np.ndarray:
        """Apply stain normalization"""
        if self.method == 'none' or self.normalizer is None:
            return image

        try:
            # Ensure image is uint8
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)

            # Apply normalization
            normalized = self.normalizer.transform(image)
            return normalized

        except Exception as e:
            print(f"Warning: Stain normalization failed: {e}. Returning original image.")
            return image


def get_aggressive_augmentation_transforms(image_size: Tuple[int, int] = (512, 512), config: Optional[dict] = None):
    """Get stronger transforms for minority classes (1.5x-2x more aggressive)"""
    if config is None:
        config = {}

    # Amplify augmentation parameters (1.5x - 2x stronger)
    transforms_list = [
        T.Resize(image_size),
        T.RandomRotation(degrees=config.get('random_rotation', 15) * 2),  # More rotation
        T.RandomHorizontalFlip(p=0.5),
        T.RandomVerticalFlip(p=0.5),
        T.RandomAffine(
            degrees=0,
            translate=(0.1, 0.1),  # Add translation
            scale=(0.9, 1.1),      # Add scaling
            shear=10               # Add shearing
        ),
    ]

    # Random crop and resize (adds more variation)
    transforms_list.append(T.RandomResizedCrop(size=image_size, scale=(0.8, 1.0)))

    # Stronger color jittering (but still conservative for medical images)
    transforms_list.append(
        GiemseStainAugmentation(
            brightness=min(config.get('brightness_jitter', 0.1) * 1.5, 0.2),
            contrast=min(config.get('contrast_jitter', 0.1) * 1.5, 0.2),
            saturation=min(config.get('saturation_jitter', 0.05) * 1.5, 0.1),
            hue=min(config.get('hue_jitter', 0.02) * 1.5, 0.05)
        )
    )

    # Higher probability gaussian blur
    transforms_list.append(T.RandomApply([T.GaussianBlur(kernel_size=3)], p=0.2))

    # Random erasing (cutout) - helps with overfitting
    transforms_list.extend([
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        T.RandomErasing(p=0.2, scale=(0.02, 0.1), ratio=(0.3, 3.3))
    ])

    return T.Compose(transforms_list)
