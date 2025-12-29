"""
Create Metadata CSV from Organized Dataset

Scans the organized dataset and creates a metadata CSV file
with all image information for training.

Usage:
    python scripts/stain_time_metadata_generator.py
    python scripts/stain_time_metadata_generator.py --data_dir data/data_04/processed --output data/data_04/splits/metadata.csv

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import argparse
from pathlib import Path
import pandas as pd
import re
from typing import Optional, Dict


def parse_filename(filename: str) -> Optional[Dict]:
    """
    Parse metadata from standardized filename

    Expected format: dilution_timemin_grade_smeartype.ext or dilution_timemin_grade_smeartype_###.ext
    Example: 10%_10min_3_thick.jpg or 10%_10min_3_thick_001.jpg
    """
    # Pattern for standardized filenames (with optional counter)
    pattern = r'(?P<dilution>\d+%)_(?P<time>\d+)min_(?P<grade>[1-5IViv]+)_(?P<smear>thin|thick)(?:_\d{3})?'

    match = re.search(pattern, filename, re.IGNORECASE)
    if match:
        metadata = match.groupdict()

        # Convert grade to numeric if it's Roman numeral
        grade_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5}
        grade_str = metadata['grade']

        if grade_str.upper() in grade_map:
            grade_numeric = grade_map[grade_str.upper()]
            grade_label = grade_str.upper()
        else:
            grade_numeric = int(grade_str)
            grade_label = ['I', 'II', 'III', 'IV', 'V'][grade_numeric - 1]

        return {
            'dilution': metadata['dilution'],
            'time_minutes': int(metadata['time']),
            'grade_numeric': grade_numeric,
            'grade_label': grade_label,
            'smear_type': metadata['smear'].lower()
        }

    return None


def stain_time_metadata_generator(data_dir: str, output_path: str):
    """
    Create metadata CSV from organized dataset

    Args:
        data_dir: Directory containing organized images
        output_path: Output CSV path
    """
    data_path = Path(data_dir)

    print("="*80)
    print("CREATING DATASET METADATA")
    print("="*80)
    print(f"Data directory: {data_path}")
    print(f"Output file: {output_path}")
    print()

    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp']
    images = []

    for ext in image_extensions:
        images.extend(data_path.glob(f'*{ext}'))

    print(f"Found {len(images)} images")
    print()

    # Parse metadata from filenames
    metadata_list = []
    failed = []

    for img_path in images:
        metadata = parse_filename(img_path.stem)

        if metadata:
            metadata['filepath'] = str(img_path)
            metadata['filename'] = img_path.name
            metadata_list.append(metadata)
        else:
            failed.append(img_path.name)

    # Create DataFrame
    df = pd.DataFrame(metadata_list)

    # Sort by dilution, time, smear
    df = df.sort_values(['dilution', 'time_minutes', 'smear_type'])

    # Save to CSV
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_file, index=False)

    print("="*80)
    print("DATASET STATISTICS")
    print("="*80)
    print(f"\nTotal images: {len(df)}")
    print(f"\nBy Dilution:")
    print(df['dilution'].value_counts().sort_index())
    print(f"\nBy Grade:")
    print(df['grade_label'].value_counts().sort_index())
    print(f"\nBy Smear Type:")
    print(df['smear_type'].value_counts())
    print()

    if failed:
        print(f"⚠️  Warning: {len(failed)} files could not be parsed:")
        for f in failed[:10]:
            print(f"   - {f}")

    print("="*80)
    print(f"✅ Metadata saved to: {output_path}")
    print(f"   Total records: {len(df)}")
    print("="*80)

    return df


def main():
    parser = argparse.ArgumentParser(
        description='Create metadata CSV from organized dataset'
    )
    parser.add_argument(
        '--data_dir',
        type=str,
        default='data/data_04/processed',
        help='Directory containing organized images'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/data_04/splits/metadata.csv',
        help='Output CSV path'
    )

    args = parser.parse_args()

    stain_time_metadata_generator(args.data_dir, args.output)


if __name__ == '__main__':
    main()
