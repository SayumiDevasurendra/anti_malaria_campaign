"""Organize and rename raw images from batch folders with metadata extraction"""

import re
import argparse
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import shutil
import pandas as pd
from collections import defaultdict


class StainTimeDatasetOrganizer:
    """Organize dataset with batch preservation and metadata extraction"""

    # Image extensions
    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}

    # Patterns to parse filenames
    PARSE_PATTERNS = [
        r'(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*smear\s*(?:grade\s*)?(?P<grade>[1-5IViv]+)',
        r'(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*(?:grade\s*)?(?P<grade>[1-5IViv]+)',
        r'(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*smear',
        r'(?P<smear>thin|thick|THIN|THICK)\s*(?P<time>\d+)\s*min\s*(?:grade\s*)?(?P<grade>[1-5IViv]+)?',
    ]

    GRADE_TO_NUMERIC = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
    }

    NUMERIC_TO_LABEL = {1: 'I', 2: 'II', 3: 'III', 4: 'IV', 5: 'V'}

    def __init__(self, raw_dir: str):
        self.raw_dir = Path(raw_dir)
        if not self.raw_dir.exists():
            raise ValueError(f"Raw directory not found: {raw_dir}")

    def find_batch_folders(self) -> List[Tuple[Path, str, str]]:
        """Find batch folders (returns: folder_path, dilution, batch_number)"""
        batch_folders = []

        for folder in self.raw_dir.iterdir():
            if not folder.is_dir():
                continue

            match = re.match(r'(\d+%?)\s*(?:batch|BATCH|Batch)\s*(\d+)', folder.name, re.IGNORECASE)
            if match:
                dilution_raw = match.group(1)
                batch_num = int(match.group(2))

                dilution = dilution_raw if dilution_raw.endswith('%') else f"{dilution_raw}%"

                batch_folders.append((folder, dilution, f"{batch_num:02d}"))

        return sorted(batch_folders, key=lambda x: (x[1], x[2]))

    def scan_images_in_folder(self, folder: Path) -> List[Path]:
        """Scan for image files in folder"""
        images = []
        for ext in self.IMAGE_EXTENSIONS:
            images.extend(folder.glob(f'*{ext}'))
            images.extend(folder.glob(f'*{ext.upper()}'))
        return sorted(set(images))

    def parse_filename(self, filename: str) -> Optional[Dict]:
        """Extract time, grade, and smear type from filename"""
        for pattern in self.PARSE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                metadata = match.groupdict()

                time = int(metadata['time'])

                grade_raw = metadata.get('grade')
                if grade_raw:
                    grade_numeric = self.GRADE_TO_NUMERIC.get(grade_raw.upper(), None)
                    grade_label = self.NUMERIC_TO_LABEL.get(grade_numeric, None) if grade_numeric else None
                else:
                    grade_numeric = None
                    grade_label = None

                smear = metadata['smear'].lower()

                return {
                    'time': time,
                    'grade_numeric': grade_numeric,
                    'grade_label': grade_label,
                    'smear': smear
                }

        return None

    def generate_new_filename(
        self,
        batch_id: str,
        dilution: str,
        time: int,
        grade_numeric: Optional[int],
        smear: str,
        extension: str
    ) -> str:
        """Generate standardized filename"""
        grade_str = str(grade_numeric) if grade_numeric else 'unknown'

        return f"batch{batch_id}_{dilution}_{time}min_{grade_str}_{smear}{extension}"

    def organize_dataset(
        self,
        processed_dir: str,
        output_csv: str,
        execute: bool = False
    ) -> pd.DataFrame:
        """Organize dataset and create metadata CSV"""
        processed_dir = Path(processed_dir)

        if execute:
            processed_dir.mkdir(parents=True, exist_ok=True)

        print("="*70)
        print("STAIN TIME DATASET ORGANIZATION")
        print("="*70)
        print(f"Raw directory: {self.raw_dir}")
        print(f"Processed directory: {processed_dir}")
        print(f"Mode: {'EXECUTE (will copy files)' if execute else 'DRY RUN (no files copied)'}")
        print("="*70)

        print("\nScanning batch folders...")
        batch_folders = self.find_batch_folders()
        print(f"Found {len(batch_folders)} batch folders:")
        for folder, dilution, batch_num in batch_folders:
            print(f"  - {folder.name} -> Batch {batch_num}, {dilution}")

        all_metadata = []
        stats = {
            'total_images': 0,
            'processed': 0,
            'failed': 0,
            'missing_grade': 0
        }

        for folder_path, dilution, batch_num in batch_folders:
            print(f"\n{'='*70}")
            print(f"Processing: {folder_path.name} (Batch {batch_num}, {dilution})")
            print(f"{'='*70}")

            images = self.scan_images_in_folder(folder_path)
            print(f"Found {len(images)} images")

            batch_processed = 0
            batch_failed = 0

            for img_path in images:
                stats['total_images'] += 1

                parsed = self.parse_filename(img_path.name)

                if not parsed:
                    print(f"  [X] SKIP: Could not parse: {img_path.name}")
                    stats['failed'] += 1
                    batch_failed += 1
                    continue

                if parsed['grade_numeric'] is None:
                    stats['missing_grade'] += 1

                new_filename = self.generate_new_filename(
                    batch_id=batch_num,
                    dilution=dilution,
                    time=parsed['time'],
                    grade_numeric=parsed['grade_numeric'],
                    smear=parsed['smear'],
                    extension=img_path.suffix.lower()
                )

                new_path = processed_dir / new_filename

                if execute and new_path.exists():
                    print(f"  [!]  CONFLICT: {new_filename} already exists!")
                    counter = 1
                    while new_path.exists():
                        new_filename_conflict = self.generate_new_filename(
                            batch_id=f"{batch_num}_{counter}",
                            dilution=dilution,
                            time=parsed['time'],
                            grade_numeric=parsed['grade_numeric'],
                            smear=parsed['smear'],
                            extension=img_path.suffix.lower()
                        )
                        new_path = processed_dir / new_filename_conflict
                        counter += 1
                    new_filename = new_filename_conflict
                    print(f"      -> Renamed to: {new_filename}")

                if execute:
                    try:
                        shutil.copy2(img_path, new_path)
                    except Exception as e:
                        print(f"  [X] ERROR copying {img_path.name}: {e}")
                        stats['failed'] += 1
                        batch_failed += 1
                        continue

                metadata_entry = {
                    'filename': str(new_path) if execute else new_filename,
                    'batch_id': f"batch{batch_num}",
                    'dilution': dilution,
                    'time_minutes': parsed['time'],
                    'grade_label': parsed['grade_label'] if parsed['grade_label'] else 'UNKNOWN',
                    'grade_numeric': parsed['grade_numeric'] if parsed['grade_numeric'] else 0,
                    'smear_type': parsed['smear'],
                    'original_filename': img_path.name,
                    'original_path': str(img_path)
                }
                all_metadata.append(metadata_entry)

                stats['processed'] += 1
                batch_processed += 1

                if batch_processed <= 3:
                    print(f"  [OK] {img_path.name}")
                    print(f"      -> {new_filename}")

            print(f"\nBatch Summary: {batch_processed} processed, {batch_failed} failed")

        df = pd.DataFrame(all_metadata)

        print(f"\n{'='*70}")
        print(f"ORGANIZATION COMPLETE")
        print(f"{'='*70}")
        print(f"Total images found: {stats['total_images']}")
        print(f"Successfully processed: {stats['processed']}")
        print(f"Failed to process: {stats['failed']}")
        print(f"Missing grade info: {stats['missing_grade']}")
        print(f"Unique batches: {df['batch_id'].nunique()}")
        print(f"Dilution methods: {df['dilution'].unique()}")
        print(f"{'='*70}")

        print(f"\nGrade Distribution by Batch:")
        for batch_id in sorted(df['batch_id'].unique()):
            batch_df = df[df['batch_id'] == batch_id]
            dilution = batch_df['dilution'].iloc[0]
            grade_counts = batch_df['grade_numeric'].value_counts().to_dict()
            print(f"  {batch_id} ({dilution}): {dict(sorted(grade_counts.items()))}")

        labeled_df = df[df['grade_label'] != 'UNKNOWN'].copy()
        unlabeled_df = df[df['grade_label'] == 'UNKNOWN'].copy()

        if len(unlabeled_df) > 0:
            print(f"\n{'='*70}")
            print(f"FILTERING UNKNOWN GRADES")
            print(f"{'='*70}")
            print(f"Found {len(unlabeled_df)} images with UNKNOWN grade")
            print(f"These will be moved to: {Path(processed_dir).parent / 'unlabeled'}")

            if execute:
                unlabeled_dir = Path(processed_dir).parent / 'unlabeled'
                unlabeled_dir.mkdir(exist_ok=True)

                for idx, row in unlabeled_df.iterrows():
                    src_path = Path(row['filename'])
                    if src_path.exists():
                        dst_path = unlabeled_dir / src_path.name
                        shutil.move(str(src_path), str(dst_path))
                        unlabeled_df.at[idx, 'filename'] = str(dst_path)

                unlabeled_csv = unlabeled_dir / 'unlabeled_metadata.csv'
                unlabeled_df.to_csv(unlabeled_csv, index=False)
                print(f"[OK] Moved {len(unlabeled_df)} unlabeled images")
                print(f"[OK] Unlabeled metadata saved to: {unlabeled_csv}")

        output_csv_path = Path(output_csv)
        if execute:
            splits_dir = output_csv_path.parent / 'splits'
            splits_dir.mkdir(exist_ok=True)
            final_csv = splits_dir / 'image_metadata.csv'

            labeled_df.to_csv(final_csv, index=False)
            print(f"\n[OK] Labeled metadata saved to: {final_csv}")
            print(f"    ({len(labeled_df)} images with valid grades)")
        else:
            print(f"\n[!]  DRY RUN: Metadata NOT saved (use --execute to save)")

        print(f"\nSample of labeled metadata:")
        sample_cols = ['filename', 'batch_id', 'dilution', 'time_minutes', 'grade_numeric', 'smear_type']
        print(labeled_df[sample_cols].head(10).to_string(index=False))

        return labeled_df


def main():
    parser = argparse.ArgumentParser(
        description="Organize stain time dataset with batch preservation"
    )

    parser.add_argument(
        '--raw-dir',
        type=str,
        required=True,
        help='Raw data directory with batch folders (e.g., "10%% Batch 1/")'
    )
    parser.add_argument(
        '--processed-dir',
        type=str,
        required=True,
        help='Output directory for processed images'
    )
    parser.add_argument(
        '--output-csv',
        type=str,
        required=True,
        help='Output CSV path for metadata'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually copy files and save metadata (without this, dry run only)'
    )

    args = parser.parse_args()

    organizer = StainTimeDatasetOrganizer(args.raw_dir)

    df = organizer.organize_dataset(
        processed_dir=args.processed_dir,
        output_csv=args.output_csv,
        execute=args.execute
    )

    print("\n" + "="*70)
    if args.execute:
        print("[OK] Organization complete! Files copied and metadata saved.")
    else:
        print("[OK] Dry run complete! Review output above, then use --execute to proceed.")
    print("="*70)


if __name__ == '__main__':
    main()
