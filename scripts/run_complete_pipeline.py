"""Complete data preparation pipeline for organizing, splitting, and optimizing datasets"""

import argparse
import subprocess
import sys
from pathlib import Path


class PipelineRunner:
    """Orchestrate complete data preparation pipeline"""

    def __init__(self, raw_dir: str, processed_dir: str, splits_dir: str, execute: bool = False):
        self.raw_dir = Path(raw_dir)
        self.processed_dir = Path(processed_dir)
        self.splits_dir = Path(splits_dir)
        self.execute = execute

        self.metadata_csv = self.splits_dir / 'image_metadata.csv'
        self.temp_splits_dir = self.splits_dir / '.temp_splits'
        self.train_csv = self.temp_splits_dir / 'train.csv'
        self.val_csv = self.temp_splits_dir / 'val.csv'
        self.test_csv = self.temp_splits_dir / 'test.csv'

        self.train_optimal_csv = self.splits_dir / 'train_optimal.csv'
        self.val_optimal_csv = self.splits_dir / 'val_optimal.csv'
        self.test_optimal_csv = self.splits_dir / 'test_optimal.csv'

    def run_command(self, cmd: list, step_name: str):
        """Execute command and handle errors"""
        print(f"\n{'='*70}")
        print(f"STEP: {step_name}")
        print(f"{'='*70}")
        print(f"Command: {' '.join(cmd)}\n")

        try:
            result = subprocess.run(cmd, check=True, capture_output=False, text=True)
            print(f"\n[OK] {step_name} completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n[X] {step_name} FAILED!")
            print(f"Error: {e}")
            return False
        except FileNotFoundError:
            print(f"\n[X] {step_name} FAILED!")
            print(f"Error: Script not found. Make sure you're in the project root directory.")
            return False

    def step1_organize_data(self):
        """Organize raw data with batch preservation"""
        cmd = [
            sys.executable,
            'scripts/organize_stain_time_dataset.py',
            '--raw-dir', str(self.raw_dir),
            '--processed-dir', str(self.processed_dir),
            '--output-csv', str(self.metadata_csv.parent / 'image_metadata_temp.csv')
        ]

        if self.execute:
            cmd.append('--execute')

        return self.run_command(cmd, "Step 1: Organize Raw Data & Filter Unknowns")

    def step2_create_splits(self):
        """Create train/val/test splits"""
        if not self.metadata_csv.exists():
            print(f"[X] Metadata CSV not found: {self.metadata_csv}")
            print(f"  Run Step 1 with --execute first!")
            return False

        cmd = [
            sys.executable,
            'scripts/create_stain_time_splits.py',
            '--input', str(self.metadata_csv),
            '--output-dir', str(self.splits_dir),
            '--train-ratio', '0.7',
            '--val-ratio', '0.15',
            '--test-ratio', '0.15',
            '--seed', '42'
        ]

        return self.run_command(cmd, "Step 2: Create Train/Val/Test Splits")

    def step3_prepare_optimal_datasets(self):
        """Prepare optimal time datasets for each split"""
        if not self.train_csv.exists():
            print(f"[X] Split CSVs not found in: {self.temp_splits_dir}")
            print(f"  Run Step 2 first!")
            return False

        print(f"\n{'='*70}")
        print("STEP 3a: Prepare Train Optimal Dataset")
        print(f"{'='*70}")

        cmd_train = [
            sys.executable,
            'scripts/prepare_stain_time_optimal_dataset.py',
            '--input', str(self.train_csv),
            '--output', str(self.train_optimal_csv)
        ]

        if not self.run_command(cmd_train, "Prepare Train Optimal"):
            return False

        print(f"\n{'='*70}")
        print("STEP 3b: Prepare Val Optimal Dataset")
        print(f"{'='*70}")

        cmd_val = [
            sys.executable,
            'scripts/prepare_stain_time_optimal_dataset.py',
            '--input', str(self.val_csv),
            '--output', str(self.val_optimal_csv)
        ]

        if not self.run_command(cmd_val, "Prepare Val Optimal"):
            return False

        print(f"\n{'='*70}")
        print("STEP 3c: Prepare Test Optimal Dataset")
        print(f"{'='*70}")

        cmd_test = [
            sys.executable,
            'scripts/prepare_stain_time_optimal_dataset.py',
            '--input', str(self.test_csv),
            '--output', str(self.test_optimal_csv)
        ]

        if not self.run_command(cmd_test, "Prepare Test Optimal"):
            return False

        import shutil
        if self.temp_splits_dir.exists():
            print(f"\n[OK] Cleaning up temporary split files...")
            shutil.rmtree(self.temp_splits_dir)
            print(f"  Removed: {self.temp_splits_dir}")

        return True

    def run_pipeline(self):
        """Execute full data preparation pipeline"""
        print("="*70)
        print("COMPLETE DATA PREPARATION PIPELINE")
        print("="*70)
        print(f"Mode: {'EXECUTE (will create files)' if self.execute else 'DRY RUN (preview only)'}")
        print(f"Raw directory: {self.raw_dir}")
        print(f"Processed directory: {self.processed_dir}")
        print(f"Splits directory: {self.splits_dir}")
        print("="*70)

        if not self.execute:
            print("\n[!]  DRY RUN MODE: No files will be created.")
            print("   Review output, then run with --execute to proceed.\n")

        steps = [
            ("Step 1: Organize Data", self.step1_organize_data),
            ("Step 2: Create Splits", self.step2_create_splits),
            ("Step 3: Prepare Optimal Datasets", self.step3_prepare_optimal_datasets)
        ]

        results = {}
        for step_name, step_func in steps:
            if self.execute or step_name == "Step 1: Organize Data":
                success = step_func()
                results[step_name] = success

                if not success and self.execute:
                    print(f"\n[X] Pipeline FAILED at {step_name}")
                    return False
            else:
                print(f"\n[!]  Skipping {step_name} (requires --execute)")
                results[step_name] = None

        print(f"\n{'='*70}")
        print("PIPELINE SUMMARY")
        print(f"{'='*70}")

        for step_name, result in results.items():
            if result is True:
                status = "[OK] SUCCESS"
            elif result is False:
                status = "[X] FAILED"
            else:
                status = "⊘ SKIPPED"
            print(f"{status}: {step_name}")

        if self.execute and all(r == True for r in results.values() if r is not None):
            print(f"\n{'='*70}")
            print("[OK] PIPELINE COMPLETE!")
            print(f"{'='*70}")
            print("\nGenerated files:")
            print(f"  1. Processed images: {self.processed_dir}/")
            print(f"  2. Filtered metadata: {self.metadata_csv}")
            print(f"  3. Final training datasets (in {self.splits_dir}/):")
            print(f"     - train_optimal.csv ({self.train_optimal_csv})")
            print(f"     - val_optimal.csv ({self.val_optimal_csv})")
            print(f"     - test_optimal.csv ({self.test_optimal_csv})")
            print(f"\nNext step: Train model using:")
            print(f"  python main_pipeline/train_grade_time_model.py \\")
            print(f"      --csv {self.train_optimal_csv} \\")
            print(f"      --checkpoint-dir checkpoints_grade_time")
            print(f"{'='*70}")
        elif not self.execute:
            print(f"\n[!]  DRY RUN COMPLETE")
            print(f"   Review output above, then run with --execute to create files")
        else:
            print(f"\n[X] PIPELINE FAILED - check errors above")

        return all(r == True for r in results.values() if r is not None)


def main():
    parser = argparse.ArgumentParser(
        description="Run complete data preparation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:

  # Dry run (preview only)
  python scripts/run_complete_pipeline.py

  # Execute full pipeline
  python scripts/run_complete_pipeline.py --execute

  # Custom directories
  python scripts/run_complete_pipeline.py \\
      --raw-dir data/data_04/raw \\
      --processed-dir data/data_04/processed \\
      --splits-dir data/data_04/splits \\
      --execute
        """
    )

    parser.add_argument(
        '--raw-dir',
        type=str,
        default='data/data_04/raw',
        help='Raw data directory with batch folders (default: data/data_04/raw)'
    )
    parser.add_argument(
        '--processed-dir',
        type=str,
        default='data/data_04/processed',
        help='Processed images directory (default: data/data_04/processed)'
    )
    parser.add_argument(
        '--splits-dir',
        type=str,
        default='data/data_04/splits',
        help='Splits directory (default: data/data_04/splits)'
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Execute pipeline (without this, dry run only)'
    )

    args = parser.parse_args()

    runner = PipelineRunner(
        raw_dir=args.raw_dir,
        processed_dir=args.processed_dir,
        splits_dir=args.splits_dir,
        execute=args.execute
    )

    success = runner.run_pipeline()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
