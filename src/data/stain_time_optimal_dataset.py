"""
Dataset for multi-task learning: Grade classification + Time recommendation

This dataset returns:
    - Image tensor
    - Grade label (0-4 for Grades I-V)
    - Current staining time
    - Time delta (optimal_time - current_time)
"""

import torch
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Optional, Callable, Tuple
import numpy as np


class StainTimeOptimalDataset(Dataset):
    """
    Dataset for training grade + time recommendation model

    Expects CSV with columns:
        - filename: Path to image file
        - grade_numeric: Grade label (1-5 for I-V, will be converted to 0-4)
        - time_minutes: Time image was stained at (minutes)
        - optimal_time: Optimal time for this batch (minutes)
        - time_delta: optimal_time - time_minutes (will be calculated if missing)
        - dilution: Dilution method (optional)
        - smear_type: Thin/thick smear (optional)
    """

    def __init__(
        self,
        csv_path: str,
        transform: Optional[Callable] = None,
        stain_normalizer: Optional[Callable] = None,
        return_metadata: bool = False
    ):
        """
        Initialize dataset

        Args:
            csv_path: Path to CSV with image metadata
            transform: Image transforms (augmentation)
            stain_normalizer: Stain normalization function
            return_metadata: Return additional metadata dict
        """
        self.csv_path = csv_path
        self.transform = transform
        self.stain_normalizer = stain_normalizer
        self.return_metadata = return_metadata

        # Load metadata
        print(f"Loading dataset from {csv_path}...")
        self.df = pd.read_csv(csv_path)

        # Validate required columns
        required_cols = ['filename', 'grade_numeric', 'time_minutes', 'optimal_time']
        missing_cols = [col for col in required_cols if col not in self.df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

        print(f"  Columns found: {list(self.df.columns)}")

        # Calculate time_delta if not present
        if 'time_delta' not in self.df.columns:
            self.df['time_delta'] = self.df['optimal_time'] - self.df['time_minutes']
            print(f"  Calculated time_delta column")

        # Verify files exist
        self._verify_files()

        print(f"Dataset loaded: {len(self.df)} images")
        print(f"  Grade distribution: {self.df['grade_numeric'].value_counts().sort_index().to_dict()}")
        print(f"  Time delta range: [{self.df['time_delta'].min():.1f}, {self.df['time_delta'].max():.1f}] minutes")

        if 'dilution' in self.df.columns:
            print(f"  Dilution types: {self.df['dilution'].unique().tolist()}")
        if 'smear_type' in self.df.columns:
            print(f"  Smear types: {self.df['smear_type'].unique().tolist()}")

    def _verify_files(self):
        """Check that image files exist"""
        missing = []
        for idx, row in self.df.iterrows():
            if not Path(row['filename']).exists():
                missing.append(row['filename'])

        if missing:
            print(f"Warning: {len(missing)} files not found")
            if len(missing) <= 5:
                for f in missing:
                    print(f"  - {f}")
            else:
                for f in missing[:5]:
                    print(f"  - {f}")
                print(f"  ... and {len(missing) - 5} more")

            # Remove missing files
            valid_mask = self.df['filename'].apply(lambda x: Path(x).exists())
            self.df = self.df[valid_mask].reset_index(drop=True)
            print(f"Dataset reduced to {len(self.df)} valid images")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple:
        """
        Get single training sample

        Returns:
            image: Transformed image tensor (C, H, W)
            grade: Grade label (0-4 for I-V, 0-indexed)
            current_time: Staining time in minutes (float)
            time_delta: Minutes to add/subtract to reach optimal (float)
            metadata: Optional dict with additional info
        """
        row = self.df.iloc[idx]

        # Load image
        image_path = Path(row['filename'])
        image = Image.open(image_path).convert('RGB')

        # Apply stain normalization (optional)
        if self.stain_normalizer is not None:
            image_np = np.array(image)
            image_np = self.stain_normalizer(image_np)
            image = Image.fromarray(image_np)

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        # Labels
        # Grade: Convert from 1-5 to 0-4 (0-indexed for CrossEntropyLoss)
        grade = int(row['grade_numeric']) - 1

        # Time information
        current_time = float(row['time_minutes'])
        time_delta = float(row['time_delta'])

        # Return
        if self.return_metadata:
            metadata = {
                'filename': str(image_path),
                'batch_id': row.get('batch_id', 'unknown'),
                'dilution': row.get('dilution', 'Unknown'),
                'smear_type': row.get('smear_type', 'unknown'),
                'grade_original': int(row['grade_numeric']),
                'optimal_time': float(row['optimal_time'])
            }
            return image, grade, current_time, time_delta, metadata
        else:
            return image, grade, current_time, time_delta

    def get_sample_weights(self) -> torch.Tensor:
        """
        Calculate sample weights for balanced training
        (grades are often imbalanced - more Grade II/III than I/V)

        Returns:
            Tensor of sample weights (one per image)
        """
        from sklearn.utils.class_weight import compute_class_weight

        grades = self.df['grade_numeric'].values

        # Compute class weights
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(grades),
            y=grades
        )

        # Create mapping from grade value to weight
        grade_to_weight = {grade: weight for grade, weight in zip(np.unique(grades), class_weights)}

        # Map to sample weights
        sample_weights = torch.tensor([grade_to_weight[g] for g in grades], dtype=torch.float32)

        return sample_weights


def collate_fn(batch):
    """
    Custom collate function for DataLoader

    Handles variable-length returns (with/without metadata)
    """
    if len(batch[0]) == 5:  # With metadata
        images, grades, current_times, time_deltas, metadata = zip(*batch)
        return (
            torch.stack(images),
            torch.tensor(grades, dtype=torch.long),
            torch.tensor(current_times, dtype=torch.float32),
            torch.tensor(time_deltas, dtype=torch.float32),
            list(metadata)
        )
    else:  # Without metadata
        images, grades, current_times, time_deltas = zip(*batch)
        return (
            torch.stack(images),
            torch.tensor(grades, dtype=torch.long),
            torch.tensor(current_times, dtype=torch.float32),
            torch.tensor(time_deltas, dtype=torch.float32)
        )


if __name__ == '__main__':
    # Test dataset loading
    import sys
    from pathlib import Path

    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))

    from src.data.stain_time_transforms import get_stain_time_val_transforms

    # Test with dummy CSV
    print("Testing StainTimeOptimalDataset...")

    # You would replace this with your actual CSV path
    csv_path = "data/data_04/image_metadata_with_optimal_times.csv"

    if Path(csv_path).exists():
        transform = get_stain_time_val_transforms(img_size=(512, 512))
        dataset = StainTimeOptimalDataset(
            csv_path=csv_path,
            transform=transform,
            return_metadata=True
        )

        print(f"\nDataset size: {len(dataset)}")

        # Test getitem
        image, grade, current_time, time_delta, metadata = dataset[0]
        print(f"\nSample 0:")
        print(f"  Image shape: {image.shape}")
        print(f"  Grade: {grade} (0-indexed)")
        print(f"  Current time: {current_time} min")
        print(f"  Time delta: {time_delta:+.1f} min")
        print(f"  Metadata: {metadata}")

        # Test DataLoader
        from torch.utils.data import DataLoader
        loader = DataLoader(
            dataset,
            batch_size=4,
            shuffle=True,
            collate_fn=collate_fn
        )

        batch = next(iter(loader))
        images, grades, current_times, time_deltas, metadata = batch
        print(f"\nBatch shapes:")
        print(f"  Images: {images.shape}")
        print(f"  Grades: {grades.shape}")
        print(f"  Current times: {current_times.shape}")
        print(f"  Time deltas: {time_deltas.shape}")

        print("\n✓ Dataset test passed!")
    else:
        print(f"CSV not found: {csv_path}")
        print("Run scripts/prepare_optimal_time_dataset.py first to create training data")
