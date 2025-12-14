"""
Stain Time Dataset Loader

Loads pre-organized slide image datasets and creates train/validation/test splits.
Assumes data has already been organized using scripts/organize_dataset.py
and metadata CSV created using scripts/create_metadata.py.

@author: Sayumi Devasurendra
@version: 0.2.0
"""

from pathlib import Path
from typing import Dict, Tuple
import pandas as pd


class StainTimeDatasetLoader:
    """Load and split pre-organized stain time dataset"""

    def __init__(self, metadata_csv: str):
        """
        Initialize dataset loader

        Args:
            metadata_csv: Path to metadata CSV file (created by scripts/create_metadata.py)
        """
        self.metadata_csv = Path(metadata_csv)
        if not self.metadata_csv.exists():
            raise FileNotFoundError(f"Metadata CSV not found: {metadata_csv}")

    def load_dataset(self) -> pd.DataFrame:
        """
        Load dataset from metadata CSV

        Returns:
            DataFrame with image metadata
        """
        print(f"Loading dataset from: {self.metadata_csv}")
        df = pd.read_csv(self.metadata_csv)
        print(f"Loaded {len(df)} images")
        return df

    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict:
        """
        Compute dataset statistics

        Args:
            df: DataFrame with metadata

        Returns:
            Dictionary of statistics
        """
        stats = {
            'total_images': len(df),
            'dilutions': df['dilution'].value_counts().to_dict(),
            'grades': df['grade_label'].value_counts().to_dict(),
            'smear_types': df['smear_type'].value_counts().to_dict(),
            'time_range': {
                dilution: {
                    'min': int(group['time_minutes'].min()),
                    'max': int(group['time_minutes'].max()),
                    'count': len(group)
                }
                for dilution, group in df.groupby('dilution')
            }
        }

        return stats

    def create_train_val_test_split(
        self,
        df: pd.DataFrame,
        train_ratio: float = 0.7,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify_by: str = 'grade_numeric',
        random_state: int = 42
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Create stratified train/validation/test split

        Args:
            df: DataFrame with metadata
            train_ratio: Proportion for training set
            val_ratio: Proportion for validation set
            test_ratio: Proportion for test set
            stratify_by: Column to stratify by
            random_state: Random seed

        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        from sklearn.model_selection import train_test_split

        assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6, "Ratios must sum to 1"

        # First split: train vs (val + test)
        train_df, temp_df = train_test_split(
            df,
            test_size=(1 - train_ratio),
            stratify=df[stratify_by],
            random_state=random_state
        )

        # Second split: val vs test
        val_size = val_ratio / (val_ratio + test_ratio)
        val_df, test_df = train_test_split(
            temp_df,
            test_size=(1 - val_size),
            stratify=temp_df[stratify_by],
            random_state=random_state
        )

        print(f"\nDataset split:")
        print(f"  Train: {len(train_df)} ({len(train_df)/len(df)*100:.1f}%)")
        print(f"  Val:   {len(val_df)} ({len(val_df)/len(df)*100:.1f}%)")
        print(f"  Test:  {len(test_df)} ({len(test_df)/len(df)*100:.1f}%)")

        return train_df, val_df, test_df
