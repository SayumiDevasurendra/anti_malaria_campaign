"""
Dataset Organization Script - Flatten and Rename

Recursively scans subdirectories, renames files to standard format,
and copies them to a single output directory.

Usage:
    python organize_dataset.py --input_dir data/raw --output_dir data/processed --dry_run
    python organize_dataset.py --input_dir data/raw --output_dir data/processed --execute

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import re
import argparse
from pathlib import Path
from typing import Optional, Dict, List
import shutil


class DatasetOrganizer:
    """Organize and rename slide image dataset"""

    # Regex patterns to extract metadata
    PARSE_PATTERNS = [
        # Pattern: "10% Batch 1 10 min thick smear Grade 3"
        r'(?P<dilution>\d+%?)\s*(?:batch|bach|BATCH|BACH)\s*\d+\s+(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*smear\s*(?:grade\s*)?(?P<grade>[1-5IViv]+)',

        # Pattern: "positive 3% batch 1 26 min thick smear grade 2"
        r'(?:positive\s+)?(?P<dilution>\d+%?)\s*(?:batch|bach|BATCH|BACH)\s*\d+[\s,]*(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*smear\s*(?:grade\s*)?(?P<grade>[1-5IViv]+)',

        # Pattern: Missing grade - "3% BATCH 1 27 MIN THICK SMEAR"
        r'(?P<dilution>\d+%?)\s*(?:batch|bach|BATCH|BACH)\s*\d+[\s,]*(?P<time>\d+)\s*min\s*(?P<smear>thin|thick|THIN|THICK)\s*smear',
    ]

    GRADE_NORMALIZE = {
        '1': '1', '2': '2', '3': '3', '4': '4', '5': '5',
        'I': 'I', 'II': 'II', 'III': 'III', 'IV': 'IV', 'V': 'V',
        'i': 'I', 'ii': 'II', 'iii': 'III', 'iv': 'IV', 'v': 'V'
    }

    GRADE_TO_NUMERIC = {
        'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
        '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
    }

    def __init__(self, input_dir: str):
        """Initialize organizer"""
        self.input_dir = Path(input_dir)
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.tif', '.tiff', '.bmp'}

    def scan_images_recursive(self) -> List[Path]:
        """Recursively scan for all image files"""
        images_set = set()  # Use set to avoid duplicates

        for ext in self.image_extensions:
            # On Windows, filesystem is case-insensitive, so lowercase is enough
            for img in self.input_dir.rglob(f'*{ext}'):
                # Skip backup directories
                if 'backup' not in str(img).lower():
                    images_set.add(img)

        return sorted(list(images_set))

    def parse_filename(self, filename: str) -> Optional[Dict]:
        """Parse metadata from filename"""
        for pattern in self.PARSE_PATTERNS:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                metadata = match.groupdict()

                # Clean dilution
                dilution = metadata['dilution']
                if not dilution.endswith('%'):
                    dilution = f"{dilution}%"

                # Normalize grade
                grade = metadata.get('grade', 'UNKNOWN')
                if grade and grade != 'UNKNOWN':
                    grade = self.GRADE_NORMALIZE.get(grade.upper(), grade)

                # Get numeric grade
                grade_numeric = self.GRADE_TO_NUMERIC.get(grade, 0)

                # Normalize smear type
                smear = metadata.get('smear', 'unknown')
                if smear:
                    smear = smear.lower()

                return {
                    'dilution': dilution,
                    'time': metadata['time'],
                    'grade': grade,
                    'grade_numeric': grade_numeric,
                    'smear': smear
                }

        return None

    def generate_new_filename(self, metadata: Dict, extension: str) -> str:
        """Generate standardized filename"""
        dilution = metadata['dilution']
        time = metadata['time']
        grade = metadata['grade']
        smear = metadata['smear']

        return f"{dilution}_{time}min_{grade}_{smear}{extension}"

    def organize_dataset(self, output_dir: str, dry_run: bool = True):
        """
        Flatten all images to single directory with renamed files

        Args:
            output_dir: Output directory path
            dry_run: If True, only preview changes
        """
        images = self.scan_images_recursive()
        output_path = Path(output_dir)

        print(f"\n📊 Dataset Summary:")
        print(f"   Input directory: {self.input_dir}")
        print(f"   Output directory: {output_path}")
        print(f"   Total images found: {len(images)}")
        print()

        if not dry_run:
            output_path.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created output directory: {output_path}\n")

        copy_count = 0
        fail_count = 0
        failed_files = []
        filename_counter = {}

        print("="*80)
        print("PROCESSING FILES")
        print("="*80)

        for img_path in images:
            filename = img_path.stem
            extension = img_path.suffix

            # Parse filename
            metadata = self.parse_filename(filename)

            if not metadata:
                print(f"✗ FAILED: {img_path.relative_to(self.input_dir)}")
                failed_files.append(img_path.name)
                fail_count += 1
                continue

            new_filename = self.generate_new_filename(metadata, extension)

            # Handle duplicate filenames by adding counter
            if new_filename in filename_counter:
                filename_counter[new_filename] += 1
                base_name = new_filename.rsplit('.', 1)[0]
                ext = new_filename.rsplit('.', 1)[1]
                new_filename = f"{base_name}_{filename_counter[new_filename]:03d}.{ext}"
            else:
                filename_counter[new_filename] = 0

            new_path = output_path / new_filename

            # Show first 20 files in detail, then just count
            if copy_count < 20:
                print(f"✓ {img_path.relative_to(self.input_dir)}")
                print(f"  → {new_filename}")
                print(f"  Metadata: dilution={metadata['dilution']}, "
                      f"time={metadata['time']}min, grade={metadata['grade']}, smear={metadata['smear']}")
                print()

            if not dry_run:
                shutil.copy2(img_path, new_path)

            copy_count += 1

        if copy_count > 20:
            print(f"... and {copy_count - 20} more files processed")

        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"✓ Successfully processed: {copy_count} files")
        print(f"✗ Failed to parse: {fail_count} files")
        print("="*80)

        if failed_files:
            print(f"\n⚠️  Failed files (need manual fixing):")
            for f in failed_files[:10]:
                print(f"   - {f}")
            if len(failed_files) > 10:
                print(f"   ... and {len(failed_files) - 10} more")

        if dry_run:
            print("\n💡 This was a DRY RUN. No files were copied.")
            print("   To execute, run with --execute flag")
        else:
            print(f"\n✅ Dataset organized successfully!")
            print(f"📁 All {copy_count} files are in: {output_path}")

        return copy_count, fail_count


def main():
    parser = argparse.ArgumentParser(
        description='Organize AMC slide image dataset - flatten and rename'
    )
    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Input directory containing image subdirectories'
    )
    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for organized dataset'
    )
    parser.add_argument(
        '--dry_run',
        action='store_true',
        help='Preview changes without executing (default)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute the organization'
    )

    args = parser.parse_args()

    # Default to dry_run unless --execute is specified
    dry_run = not args.execute

    print("="*80)
    print("AMC DATASET ORGANIZATION TOOL")
    print("="*80)
    print(f"Mode: {'EXECUTE' if not dry_run else 'DRY RUN (preview only)'}")
    print("="*80)

    organizer = DatasetOrganizer(args.input_dir)
    organizer.organize_dataset(args.output_dir, dry_run=dry_run)


if __name__ == '__main__':
    main()
