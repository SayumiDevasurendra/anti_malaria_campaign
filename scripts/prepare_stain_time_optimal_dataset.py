"""Prepare optimal time dataset by finding when both thin and thick smears reach Grade 3"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import Optional


def find_optimal_time_both_smears(batch_df: pd.DataFrame, verbose: bool = False) -> Optional[int]:
    """Find earliest time where both thin and thick smears reach Grade 3"""
    time_groups = batch_df.groupby('time_minutes')

    optimal_candidates = []

    for time, time_df in time_groups:
        smear_types = time_df['smear_type'].unique()

        grades_by_smear = {}
        for smear in smear_types:
            smear_grades = time_df[time_df['smear_type'] == smear]['grade_numeric'].values
            grades_by_smear[smear] = smear_grades

        is_optimal = False

        if len(smear_types) == 2:
            thin_has_grade3 = 3 in grades_by_smear.get('thin', [])
            thick_has_grade3 = 3 in grades_by_smear.get('thick', [])

            if thin_has_grade3 and thick_has_grade3:
                is_optimal = True
                if verbose:
                    print(f"      {time} min: thin=3 [OK], thick=3 [OK] -> OPTIMAL")
        elif len(smear_types) == 1:
            smear = smear_types[0]
            if 3 in grades_by_smear[smear]:
                is_optimal = True
                if verbose:
                    print(f"      {time} min: {smear}=3 [OK] (only smear type) -> OPTIMAL")

        if is_optimal:
            optimal_candidates.append(time)
        elif verbose:
            grade_str = ', '.join([f"{s}={list(g)}" for s, g in grades_by_smear.items()])
            print(f"      {time} min: {grade_str}")

    if len(optimal_candidates) == 0:
        return None

    return min(optimal_candidates)


def prepare_optimal_time_dataset(
    input_csv: str,
    output_csv: str,
    verbose: bool = False
):
    """Add optimal_time and time_delta columns to dataset"""
    print("="*70)
    print("PREPARING OPTIMAL TIME DATASET")
    print("="*70)
    print(f"Input: {input_csv}")
    print(f"Output: {output_csv}")
    print("="*70)

    df = pd.read_csv(input_csv)
    print(f"\nLoaded {len(df)} images")

    if 'batch_id' not in df.columns:
        raise ValueError("Input CSV must have 'batch_id' column! Run organize_stain_time_dataset.py first.")

    print(f"Total batches: {df['batch_id'].nunique()}")

    print(f"\n{'='*70}")
    print("FINDING OPTIMAL TIMES (BOTH THIN + THICK MUST BE GRADE 3)")
    print(f"{'='*70}\n")

    optimal_times = {}
    batch_stats = []

    for batch_id, batch_df in df.groupby('batch_id'):
        batch_df = batch_df.sort_values('time_minutes')

        dilution = batch_df['dilution'].iloc[0]
        time_range = f"{batch_df['time_minutes'].min()}-{batch_df['time_minutes'].max()}"
        smear_types = sorted(batch_df['smear_type'].unique())

        print(f"{batch_id} ({dilution}, {len(batch_df)} images, {time_range} min, smears: {smear_types})")

        optimal_time = find_optimal_time_both_smears(batch_df, verbose=verbose)

        optimal_times[batch_id] = optimal_time

        stats = {
            'batch_id': batch_id,
            'dilution': dilution,
            'num_images': len(batch_df),
            'time_range': time_range,
            'smear_types': '+'.join(smear_types),
            'optimal_time': optimal_time,
            'has_optimal': optimal_time is not None
        }
        batch_stats.append(stats)

        if optimal_time is not None:
            print(f"  [OK] Optimal time: {optimal_time} min\n")
        else:
            print(f"  [X] NO OPTIMAL TIME FOUND")
            print(f"      No timepoint has BOTH thin AND thick as Grade 3")
            print(f"      Grade distribution:")
            for (time, smear), grades in batch_df.groupby(['time_minutes', 'smear_type'])['grade_numeric'].apply(list).items():
                print(f"        {time} min ({smear}): {grades}")
            print()

    df['optimal_time'] = df['batch_id'].map(optimal_times)
    df['time_delta'] = df['optimal_time'] - df['time_minutes']

    df_with_optimal = df[df['optimal_time'].notna()].copy()

    print(f"{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Total images: {len(df)}")
    print(f"Images with optimal time: {len(df_with_optimal)} ({len(df_with_optimal)/len(df):.1%})")
    print(f"Total batches: {df['batch_id'].nunique()}")
    print(f"Batches with optimal time: {sum(1 for s in batch_stats if s['has_optimal'])}")
    print(f"Batches WITHOUT optimal time: {sum(1 for s in batch_stats if not s['has_optimal'])}")
    print(f"{'='*70}")

    failed_batches = [s for s in batch_stats if not s['has_optimal']]
    if failed_batches:
        print(f"\n[!]  WARNING: {len(failed_batches)} batches have NO optimal time:")
        for stats in failed_batches:
            print(f"  {stats['batch_id']} ({stats['dilution']}): {stats['time_range']} min, smears: {stats['smear_types']}")
        print("\n  These batches are EXCLUDED from training dataset.")
        print("  Check if images are missing or mislabeled.\n")

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    df_with_optimal.to_csv(output_csv, index=False)
    print(f"[OK] Training dataset saved: {output_csv}")

    print(f"\nSample of prepared dataset:")
    sample_cols = ['filename', 'batch_id', 'dilution', 'smear_type', 'time_minutes', 'grade_numeric', 'optimal_time', 'time_delta']
    available_cols = [c for c in sample_cols if c in df_with_optimal.columns]
    print(df_with_optimal[available_cols].head(10).to_string(index=False))

    print(f"\n[OK] Dataset preparation complete!")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare optimal time dataset for training"
    )

    parser.add_argument('--input', type=str, required=True, help='Input metadata CSV with batch_id')
    parser.add_argument('--output', type=str, required=True, help='Output CSV with optimal times')
    parser.add_argument('--verbose', action='store_true', help='Show detailed batch processing')

    args = parser.parse_args()

    prepare_optimal_time_dataset(
        input_csv=args.input,
        output_csv=args.output,
        verbose=args.verbose
    )


if __name__ == '__main__':
    main()
