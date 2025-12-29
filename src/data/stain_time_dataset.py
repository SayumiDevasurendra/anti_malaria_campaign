"""PyTorch datasets for Giemsa-stained slide images"""

import torch
from torch.utils.data import Dataset
from PIL import Image
import pandas as pd
from pathlib import Path
from typing import Optional, Callable, Dict, Tuple
import numpy as np


class StainTimeDataset(Dataset):
    """Dataset for Giemsa-stained slide images with stain time metadata"""

    def __init__(
        self,
        metadata_df: pd.DataFrame,
        transform: Optional[Callable] = None,
        stain_normalizer: Optional[Callable] = None,
        return_metadata: bool = False
    ):
        self.metadata_df = metadata_df.reset_index(drop=True)
        self.transform = transform
        self.stain_normalizer = stain_normalizer
        self.return_metadata = return_metadata

        # Verify all files exist
        self._verify_files()

    def _verify_files(self):
        """Verify that all image files exist"""
        # Determine which column has file paths
        filepath_col = 'filepath' if 'filepath' in self.metadata_df.columns else 'filename'

        missing = []
        for idx, row in self.metadata_df.iterrows():
            if not Path(row[filepath_col]).exists():
                missing.append(row[filepath_col])

        if missing:
            print(f"Warning: {len(missing)} files not found:")
            for f in missing[:5]:
                print(f"  - {f}")
            if len(missing) > 5:
                print(f"  ... and {len(missing) - 5} more")

            # Remove missing files
            valid_mask = self.metadata_df[filepath_col].apply(lambda x: Path(x).exists())
            self.metadata_df = self.metadata_df[valid_mask].reset_index(drop=True)
            print(f"Dataset reduced to {len(self.metadata_df)} valid images")

    def __len__(self) -> int:
        return len(self.metadata_df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, Optional[Dict]]:
        """Get item: (image_tensor, grade_label, optional_metadata)"""
        # Get metadata
        row = self.metadata_df.iloc[idx]

        # Load image (handle both 'filepath' and 'filename' columns)
        filepath_col = 'filepath' if 'filepath' in row else 'filename'
        image_path = Path(row[filepath_col])
        image = Image.open(image_path).convert('RGB')

        # Apply stain normalization if enabled
        if self.stain_normalizer is not None:
            image_np = np.array(image)
            image_np = self.stain_normalizer(image_np)
            image = Image.fromarray(image_np)

        # Apply transforms
        if self.transform:
            image = self.transform(image)

        # Grade label (0-indexed: 0=Grade I, 4=Grade V)
        grade = int(row['grade_numeric']) - 1

        # Return with or without metadata
        if self.return_metadata:
            metadata = {
                'dilution': row['dilution'],
                'time_minutes': row['time_minutes'],
                'grade_numeric': row['grade_numeric'],
                'grade_label': row['grade_label'],
                'smear_type': row['smear_type'],
                'filename': row['filename']
            }
            return image, grade, metadata
        else:
            return image, grade


class StainTimeMultiTaskDataset(StainTimeDataset):
    """Dataset for multi-task learning (grade + failure reasons)"""

    # Failure reason indices
    REASON_CODES = {
        'under_stain': 0,
        'over_stain': 1,
        'precipitates': 2,
        'ph_rinse_issue': 3,
        'fixation_problem': 4,
        'background_artefacts': 5
    }

    def __init__(
        self,
        metadata_df: pd.DataFrame,
        transform: Optional[Callable] = None,
        stain_normalizer: Optional[Callable] = None,
        return_metadata: bool = False,
        reason_columns: Optional[list] = None
    ):
        super().__init__(metadata_df, transform, stain_normalizer, return_metadata)

        # Default reason columns if not provided
        if reason_columns is None:
            self.reason_columns = list(self.REASON_CODES.keys())
        else:
            self.reason_columns = reason_columns

        # Verify reason columns exist
        for col in self.reason_columns:
            if col not in self.metadata_df.columns:
                # Add column with zeros if missing
                self.metadata_df[col] = 0
                print(f"Warning: Reason column '{col}' not found. Initialized with zeros.")

    def __getitem__(self, idx: int):
        """Get item with multi-task labels (image, grade, reason_labels, metadata)"""
        # Get image and grade from parent class
        if self.return_metadata:
            image, grade, metadata = super().__getitem__(idx)
        else:
            image, grade = super().__getitem__(idx)
            metadata = None

        # Get reason labels (multi-label binary vector)
        row = self.metadata_df.iloc[idx]
        reason_labels = torch.tensor(
            [int(row[col]) for col in self.reason_columns],
            dtype=torch.float32
        )

        if self.return_metadata:
            return image, grade, reason_labels, metadata
        else:
            return image, grade, reason_labels
