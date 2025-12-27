"""
Balanced Dataset with Targeted Augmentation

Custom dataset class that applies stronger augmentation to minority classes
to help balance the training distribution.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import torch
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Optional, Callable, Dict, Tuple
import numpy as np


class BalancedStainTimeDataset(Dataset):
    """
    Dataset with targeted augmentation for minority classes

    Applies stronger data augmentation to underrepresented grades
    to synthetically increase their diversity.
    """

    def __init__(
        self,
        metadata_df: pd.DataFrame,
        base_transform: Optional[Callable] = None,
        minority_transform: Optional[Callable] = None,
        stain_normalizer: Optional[Callable] = None,
        minority_classes: Optional[list] = None,
        return_metadata: bool = False
    ):
        """
        Initialize balanced dataset with targeted augmentation

        Args:
            metadata_df: DataFrame with image metadata
            base_transform: Standard transformations for all images
            minority_transform: Stronger augmentation for minority classes
            stain_normalizer: Optional stain normalization
            minority_classes: List of class indices to apply stronger augmentation
                             If None, automatically detects based on distribution
            return_metadata: Whether to return full metadata dict
        """
        self.metadata_df = metadata_df.reset_index(drop=True)
        self.base_transform = base_transform
        self.minority_transform = minority_transform
        self.stain_normalizer = stain_normalizer
        self.return_metadata = return_metadata

        # Determine minority classes if not provided
        if minority_classes is None:
            self.minority_classes = self._identify_minority_classes()
        else:
            self.minority_classes = minority_classes

        # Verify all files exist
        self._verify_files()

        print(f"Balanced Dataset initialized:")
        print(f"  Total samples: {len(self.metadata_df)}")
        print(f"  Minority classes (stronger aug): {self.minority_classes}")

    def _identify_minority_classes(self, threshold_percentile: int = 40) -> list:
        """
        Automatically identify minority classes based on sample count

        Args:
            threshold_percentile: Classes below this percentile are considered minority

        Returns:
            List of minority class indices (0-indexed)
        """
        # Get grade distribution (grades are 1-5, need to convert to 0-4 for indices)
        grade_counts = self.metadata_df['grade_numeric'].value_counts()

        # Calculate threshold
        threshold = np.percentile(list(grade_counts.values), threshold_percentile)

        # Identify minority classes
        minority_grades = [grade for grade, count in grade_counts.items() if count < threshold]

        # Convert to 0-indexed (Grade 2 -> index 1, Grade 3 -> index 2, etc.)
        minority_indices = [grade - 1 for grade in minority_grades]

        return minority_indices

    def _verify_files(self):
        """Verify that all image files exist"""
        missing = []
        for idx, row in self.metadata_df.iterrows():
            filepath = row.get('filepath', row.get('filename', ''))
            if not Path(filepath).exists():
                missing.append(filepath)

        if missing:
            print(f"Warning: {len(missing)} files not found:")
            for f in missing[:5]:
                print(f"  - {f}")
            if len(missing) > 5:
                print(f"  ... and {len(missing) - 5} more")

            # Remove missing files
            filepath_col = 'filepath' if 'filepath' in self.metadata_df.columns else 'filename'
            valid_mask = self.metadata_df[filepath_col].apply(lambda x: Path(x).exists())
            self.metadata_df = self.metadata_df[valid_mask].reset_index(drop=True)
            print(f"Dataset reduced to {len(self.metadata_df)} valid images")

    def __len__(self) -> int:
        return len(self.metadata_df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, Optional[Dict]]:
        """
        Get item from dataset with targeted augmentation

        Args:
            idx: Index

        Returns:
            Tuple of (image_tensor, grade_label, metadata_dict)
        """
        # Get metadata
        row = self.metadata_df.iloc[idx]

        # Load image
        filepath_col = 'filepath' if 'filepath' in row else 'filename'
        image_path = Path(row[filepath_col])
        image = Image.open(image_path).convert('RGB')

        # Apply stain normalization if enabled
        if self.stain_normalizer is not None:
            image_np = np.array(image)
            image_np = self.stain_normalizer(image_np)
            image = Image.fromarray(image_np)

        # Grade label (0-indexed: 0=Grade I, 4=Grade V)
        grade_numeric = int(row['grade_numeric'])
        grade = grade_numeric - 1  # Convert to 0-indexed

        # Apply targeted augmentation for minority classes
        if grade in self.minority_classes and self.minority_transform is not None:
            # Use stronger augmentation for minority classes
            image = self.minority_transform(image)
        elif self.base_transform is not None:
            # Use standard augmentation for majority classes
            image = self.base_transform(image)

        # Return with or without metadata
        if self.return_metadata:
            metadata = {
                'dilution': row['dilution'],
                'time_minutes': row['time_minutes'],
                'grade_numeric': grade_numeric,
                'grade_label': row.get('grade_label', str(grade_numeric)),
                'smear_type': row['smear_type'],
                'filename': str(image_path),
                'is_minority_class': grade in self.minority_classes
            }
            return image, grade, metadata
        else:
            return image, grade


class HybridBalancedDataset(Dataset):
    """
    Hybrid dataset that combines weighted sampling with targeted augmentation

    This dataset is designed to work with WeightedRandomSampler AND apply
    stronger augmentation to minority classes for maximum balance.
    """

    def __init__(
        self,
        metadata_df: pd.DataFrame,
        base_transform: Optional[Callable] = None,
        minority_transform: Optional[Callable] = None,
        stain_normalizer: Optional[Callable] = None,
        minority_classes: Optional[list] = None,
        augmentation_multiplier: int = 2,
        return_metadata: bool = False
    ):
        """
        Initialize hybrid balanced dataset

        Args:
            metadata_df: DataFrame with image metadata
            base_transform: Standard transformations for all images
            minority_transform: Stronger augmentation for minority classes
            stain_normalizer: Optional stain normalization
            minority_classes: List of class indices to apply stronger augmentation
            augmentation_multiplier: How many times to repeat minority class samples
                                    (synthetically increases their representation)
            return_metadata: Whether to return full metadata dict
        """
        self.original_df = metadata_df.reset_index(drop=True)
        self.base_transform = base_transform
        self.minority_transform = minority_transform
        self.stain_normalizer = stain_normalizer
        self.return_metadata = return_metadata
        self.augmentation_multiplier = augmentation_multiplier

        # Determine minority classes
        if minority_classes is None:
            self.minority_classes = self._identify_minority_classes()
        else:
            self.minority_classes = minority_classes

        # Create augmented dataset by repeating minority samples
        self.metadata_df = self._create_augmented_dataset()

        print(f"Hybrid Balanced Dataset initialized:")
        print(f"  Original samples: {len(self.original_df)}")
        print(f"  Augmented samples: {len(self.metadata_df)}")
        print(f"  Minority classes: {self.minority_classes}")
        print(f"  Augmentation multiplier: {augmentation_multiplier}x")

    def _identify_minority_classes(self, threshold_percentile: int = 40) -> list:
        """Identify minority classes based on distribution"""
        grade_counts = self.original_df['grade_numeric'].value_counts()
        threshold = np.percentile(list(grade_counts.values), threshold_percentile)
        minority_grades = [grade for grade, count in grade_counts.items() if count < threshold]
        return [grade - 1 for grade in minority_grades]

    def _create_augmented_dataset(self) -> pd.DataFrame:
        """
        Create augmented dataset by repeating minority class samples

        Returns:
            Augmented DataFrame
        """
        dfs = [self.original_df]  # Start with original

        # Add copies of minority class samples
        for _ in range(self.augmentation_multiplier - 1):
            minority_mask = self.original_df['grade_numeric'].apply(
                lambda x: (x - 1) in self.minority_classes
            )
            minority_df = self.original_df[minority_mask].copy()
            dfs.append(minority_df)

        # Concatenate and shuffle
        augmented_df = pd.concat(dfs, ignore_index=True)
        augmented_df = augmented_df.sample(frac=1, random_state=42).reset_index(drop=True)

        return augmented_df

    def __len__(self) -> int:
        return len(self.metadata_df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, Optional[Dict]]:
        """Get item with targeted augmentation"""
        # Get metadata
        row = self.metadata_df.iloc[idx]

        # Load image
        filepath_col = 'filepath' if 'filepath' in row else 'filename'
        image_path = Path(row[filepath_col])
        image = Image.open(image_path).convert('RGB')

        # Apply stain normalization if enabled
        if self.stain_normalizer is not None:
            image_np = np.array(image)
            image_np = self.stain_normalizer(image_np)
            image = Image.fromarray(image_np)

        # Grade label (0-indexed)
        grade_numeric = int(row['grade_numeric'])
        grade = grade_numeric - 1

        # Apply targeted augmentation for minority classes
        if grade in self.minority_classes and self.minority_transform is not None:
            image = self.minority_transform(image)
        elif self.base_transform is not None:
            image = self.base_transform(image)

        # Return
        if self.return_metadata:
            metadata = {
                'dilution': row['dilution'],
                'time_minutes': row['time_minutes'],
                'grade_numeric': grade_numeric,
                'grade_label': row.get('grade_label', str(grade_numeric)),
                'smear_type': row['smear_type'],
                'filename': str(image_path),
                'is_minority_class': grade in self.minority_classes
            }
            return image, grade, metadata
        else:
            return image, grade
