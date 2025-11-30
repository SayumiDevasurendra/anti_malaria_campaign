"""
Stain Time Dataset Organization Module

Handles scanning, parsing, and organizing Giemsa-stained slide images.
Extracts metadata from filenames and creates train/validation/test splits.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
from tqdm import tqdm


class StainTimeDatasetOrganizer:
    """Organize and parse stain time optimization image dataset"""

    # Filename patterns to extract metadata
    PATTERNS = [
        # Pattern 1: dilution_batchN_time_grade_smear.ext (with batch number)
        # Example: 10%_batch1_8min_3_thin.jpg
        r'(?P<dilution>\d+%)_batch(?P<batch>\d+)_(?P<time>\d+)min_(?P<grade>[IV]+|[1-5])_(?P<smear>thin|thick)',

        # Pattern 2: dilution_time_grade_smear.ext (without batch)
        # Example: 10%_8min_III_thin.jpg
        r'(?P<dilution>\d+%)_(?P<time>\d+)min_(?P<grade>[IV]+|[1-5])_(?P<smear>thin|thick)',

        # Pattern 3: dilution_time_grade.ext
        # Example: 3%_35min_IV.jpg
        r'(?P<dilution>\d+%)_(?P<time>\d+)min_(?P<grade>[IV]+|[1-5])',

        # Pattern 4: More flexible with separators
        # Example: 10pct-8-III-thin.jpg
        r'(?P<dilution>\d+)(?:pct|%)[-_](?P<time>\d+)[-_](?P<grade>[IV]+|[1-5])[-_]?(?P<smear>thin|thick)?',
    ]

    GRADE_MAPPING = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
    }

    def __init__(self, data_dir: str):
        """
        Initialize dataset organizer

        Args:
            data_dir: Root directory containing slide images
        """
        self.data_dir = Path(data_dir)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}

    def scan_images(self) -> List[Path]:
        """
        Scan directory for image files

        Returns:
            List of image file paths
        """
        images = []
        for ext in self.image_extensions:
            images.extend(self.data_dir.rglob(f'*{ext}'))
        return sorted(images)

    def parse_filename(self, filepath: Path) -> Optional[Dict]:
        """
        Extract metadata from filename

        Args:
            filepath: Path to image file

        Returns:
            Dictionary with metadata or None if parsing fails
        """
        filename = filepath.stem

        for pattern in self.PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                metadata = match.groupdict()

                # Clean dilution (ensure format is "10%" or "3%")
                dilution = metadata['dilution']
                if not dilution.endswith('%'):
                    dilution = f"{dilution}%"
                metadata['dilution'] = dilution

                # Convert time to integer
                metadata['time_minutes'] = int(metadata['time'])

                # Convert grade to numeric (1-5)
                grade_str = metadata['grade'].upper()
                metadata['grade_numeric'] = self.GRADE_MAPPING.get(grade_str)
                metadata['grade_label'] = grade_str if grade_str in ['I', 'II', 'III', 'IV', 'V'] else str(metadata['grade_numeric'])

                # Smear type (default to unknown if not present)
                metadata['smear_type'] = metadata.get('smear', 'unknown')

                # Add file info
                metadata['filepath'] = str(filepath)
                metadata['filename'] = filepath.name

                return metadata

        return None

    def organize_dataset(self, output_csv: Optional[str] = None) -> pd.DataFrame:
        """
        Scan and organize entire dataset

        Args:
            output_csv: Optional path to save metadata CSV

        Returns:
            DataFrame with image metadata
        """
        print("Scanning for images...")
        image_paths = self.scan_images()
        print(f"Found {len(image_paths)} images")

        print("\nParsing filenames...")
        metadata_list = []
        failed_files = []

        for img_path in tqdm(image_paths):
            metadata = self.parse_filename(img_path)
            if metadata:
                metadata_list.append(metadata)
            else:
                failed_files.append(img_path.name)

        # Create DataFrame
        df = pd.DataFrame(metadata_list)

        # Report results
        print(f"\n✓ Successfully parsed: {len(metadata_list)} files")
        print(f"✗ Failed to parse: {len(failed_files)} files")

        if failed_files:
            print("\nFailed files (first 10):")
            for f in failed_files[:10]:
                print(f"  - {f}")

        # Save to CSV
        if output_csv and len(df) > 0:
            output_path = Path(output_csv)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(output_path, index=False)
            print(f"\n✓ Metadata saved to: {output_csv}")

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
