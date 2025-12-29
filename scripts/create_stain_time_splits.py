"""Create train/val/test splits with batch integrity preservation"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from sklearn.model_selection import train_test_split
from collections import defaultdict


def create_splits(
    input_csv: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
):
    """Create stratified splits ensuring batches stay together"""
    if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
        raise ValueError(f"Split ratios must sum to 1.0, got {train_ratio + val_ratio + test_ratio}")

    # Load and validate data
    print("="*70)
    print("CREATING TRAIN/VAL/TEST SPLITS")
    print("="*70)
    print(f"Input: {input_csv}")
    print(f"Output directory: {output_dir}")
    print(f"Split ratios: Train={train_ratio:.0%}, Val={val_ratio:.0%}, Test={test_ratio:.0%}")
    print(f"Random seed: {seed}")
    print("="*70)

    df = pd.read_csv(input_csv)

    # Remove images with invalid grades
    initial_count = len(df)
    df = df[df['grade_label'] != 'UNKNOWN'].copy()
    df = df[df['grade_numeric'] > 0].copy()

    if len(df) < initial_count:
        print(f"\n[!] Filtered out {initial_count - len(df)} images with unknown grades")

    print(f"\nTotal images: {len(df)}")
    print(f"Unique batches: {df['batch_id'].nunique()}")

    np.random.seed(seed)

    batch_groups = df.groupby('batch_id')

    # Calculate batch statistics for stratification
    batch_stats = []
    for batch_id, batch_df in batch_groups:
        stats = {
            'batch_id': batch_id,
            'dilution': batch_df['dilution'].iloc[0],
            'num_images': len(batch_df),
            'num_grade3': (batch_df['grade_numeric'] == 3).sum(),
            'has_grade3': (batch_df['grade_numeric'] == 3).any(),
            'mean_grade': batch_df['grade_numeric'].mean()
        }
        batch_stats.append(stats)

    batch_stats_df = pd.DataFrame(batch_stats)

    # Create stratification key: dilution + has_grade3
    batch_stats_df['strat_key'] = (
        batch_stats_df['dilution'].astype(str) + '_' +
        batch_stats_df['has_grade3'].astype(str)
    )

    print(f"\nBatch stratification:")
    print(batch_stats_df.groupby('strat_key').size())

    # Split batches (stratified by dilution + grade3 presence)
    try:
        train_batches, temp_batches = train_test_split(
            batch_stats_df['batch_id'].values,
            test_size=(val_ratio + test_ratio),
            stratify=batch_stats_df['strat_key'].values,
            random_state=seed
        )
        print(f"\n[OK] Using stratified split by {batch_stats_df['strat_key'].unique()}")
    except ValueError as e:
        print(f"\n[!]  Stratification failed (too few batches per group): {e}")
        print(f"   Falling back to simple random split...")
        train_batches, temp_batches = train_test_split(
            batch_stats_df['batch_id'].values,
            test_size=(val_ratio + test_ratio),
            random_state=seed
        )

    temp_batch_stats = batch_stats_df[batch_stats_df['batch_id'].isin(temp_batches)]

    try:
        val_batches, test_batches = train_test_split(
            temp_batch_stats['batch_id'].values,
            test_size=(test_ratio / (val_ratio + test_ratio)),
            stratify=temp_batch_stats['strat_key'].values,
            random_state=seed
        )
    except ValueError as e:
        print(f"[!]  Stratification failed for val/test split: {e}")
        print(f"   Using simple random split for val/test...")
        val_batches, test_batches = train_test_split(
            temp_batch_stats['batch_id'].values,
            test_size=(test_ratio / (val_ratio + test_ratio)),
            random_state=seed
        )

    df['split'] = 'train'  # default
    df.loc[df['batch_id'].isin(val_batches), 'split'] = 'val'
    df.loc[df['batch_id'].isin(test_batches), 'split'] = 'test'

    train_df = df[df['split'] == 'train'].copy()
    val_df = df[df['split'] == 'val'].copy()
    test_df = df[df['split'] == 'test'].copy()

    print(f"\n{'='*70}")
    print("SPLIT STATISTICS")
    print(f"{'='*70}")
    print(f"\nTrain:")
    print(f"  Batches: {train_df['batch_id'].nunique()}")
    print(f"  Images: {len(train_df)} ({len(train_df)/len(df):.1%})")
    print(f"  Grade distribution: {dict(train_df['grade_numeric'].value_counts().sort_index())}")
    print(f"  Dilution: {dict(train_df['dilution'].value_counts())}")

    print(f"\nValidation:")
    print(f"  Batches: {val_df['batch_id'].nunique()}")
    print(f"  Images: {len(val_df)} ({len(val_df)/len(df):.1%})")
    print(f"  Grade distribution: {dict(val_df['grade_numeric'].value_counts().sort_index())}")
    print(f"  Dilution: {dict(val_df['dilution'].value_counts())}")

    print(f"\nTest:")
    print(f"  Batches: {test_df['batch_id'].nunique()}")
    print(f"  Images: {len(test_df)} ({len(test_df)/len(df):.1%})")
    print(f"  Grade distribution: {dict(test_df['grade_numeric'].value_counts().sort_index())}")
    print(f"  Dilution: {dict(test_df['dilution'].value_counts())}")

    # Save temporary splits
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    temp_dir = output_dir / '.temp_splits'
    temp_dir.mkdir(exist_ok=True)

    train_path = temp_dir / 'train.csv'
    val_path = temp_dir / 'val.csv'
    test_path = temp_dir / 'test.csv'

    train_df = train_df.drop(columns=['split'])
    val_df = val_df.drop(columns=['split'])
    test_df = test_df.drop(columns=['split'])

    train_df.to_csv(train_path, index=False)
    val_df.to_csv(val_path, index=False)
    test_df.to_csv(test_path, index=False)

    print(f"\n{'='*70}")
    print(f"[OK] Intermediate splits saved to temp directory")
    print(f"  (These will be converted to optimal CSVs in next step)")
    print(f"{'='*70}")

    # Verify batch integrity
    print(f"\nVerifying batch integrity...")
    all_batches = set(df['batch_id'].unique())
    train_batches_set = set(train_df['batch_id'].unique())
    val_batches_set = set(val_df['batch_id'].unique())
    test_batches_set = set(test_df['batch_id'].unique())

    overlaps = []
    if train_batches_set & val_batches_set:
        overlaps.append(f"Train-Val overlap: {train_batches_set & val_batches_set}")
    if train_batches_set & test_batches_set:
        overlaps.append(f"Train-Test overlap: {train_batches_set & test_batches_set}")
    if val_batches_set & test_batches_set:
        overlaps.append(f"Val-Test overlap: {val_batches_set & test_batches_set}")

    if overlaps:
        print("  [X] ERROR: Batch overlap detected!")
        for overlap in overlaps:
            print(f"    {overlap}")
    else:
        print("  [OK] No batch overlap - all batches assigned to single split")

    assigned = train_batches_set | val_batches_set | test_batches_set
    if assigned == all_batches:
        print("  [OK] All batches assigned to a split")
    else:
        missing = all_batches - assigned
        print(f"  [X] WARNING: {len(missing)} batches not assigned: {missing}")

    print(f"\n[OK] Split creation complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Create train/val/test splits for stain time dataset"
    )

    parser.add_argument('--input', type=str, required=True, help='Input metadata CSV')
    parser.add_argument('--output-dir', type=str, required=True, help='Output directory for splits')
    parser.add_argument('--train-ratio', type=float, default=0.7, help='Train split ratio (default: 0.7)')
    parser.add_argument('--val-ratio', type=float, default=0.15, help='Validation split ratio (default: 0.15)')
    parser.add_argument('--test-ratio', type=float, default=0.15, help='Test split ratio (default: 0.15)')
    parser.add_argument('--seed', type=int, default=42, help='Random seed (default: 42)')

    args = parser.parse_args()

    create_splits(
        input_csv=args.input,
        output_dir=args.output_dir,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed
    )


if __name__ == '__main__':
    main()
