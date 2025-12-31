"""Prepare optimal time dataset by finding when both thin and thick smears reach Grade 3"""

import pandas as pd
import numpy as np
from pathlib import Path
import argparse
from typing import Optional


def find_optimal_time_both_smears(batch_df: pd.DataFrame, dilution: str, verbose: bool = False) -> Optional[int]:
    """
    Logic:
    1. First priority: Find earliest timestamp where BOTH thin AND thick have Grade 3 at the same time
    2. Second priority (fallback): If no such timestamp exists, find earliest timestamp where
       at least one smear type has Grade 3 (when the other smear type doesn't have Grade 3 anywhere)
    3. Apply rounding for 3% dilution to ensure times are in expected range (30-45 min)
    """
    # First, identify which smear types have Grade 3 anywhere in the batch
    thin_df = batch_df[batch_df['smear_type'] == 'thin']
    thick_df = batch_df[batch_df['smear_type'] == 'thick']

    batch_has_thin = len(thin_df) > 0
    batch_has_thick = len(thick_df) > 0

    thin_has_grade3_anywhere = (thin_df['grade_numeric'] == 3).any() if batch_has_thin else False
    thick_has_grade3_anywhere = (thick_df['grade_numeric'] == 3).any() if batch_has_thick else False

    if verbose:
        print(f"      Batch summary:")
        print(f"        Has thin smears: {batch_has_thin}, thin has Grade 3: {thin_has_grade3_anywhere}")
        print(f"        Has thick smears: {batch_has_thick}, thick has Grade 3: {thick_has_grade3_anywhere}")

    # Group by time to find candidates
    time_groups = batch_df.groupby('time_minutes')

    # Priority 1: Find timestamps where BOTH thin AND thick have Grade 3 simultaneously
    both_smears_optimal_candidates = []

    # Priority 2: Find timestamps where at least one smear has Grade 3 (fallback)
    single_smear_optimal_candidates = []

    for time, time_df in time_groups:
        smear_types_at_time = time_df['smear_type'].unique()

        grades_by_smear = {}
        for smear in smear_types_at_time:
            smear_grades = time_df[time_df['smear_type'] == smear]['grade_numeric'].values
            grades_by_smear[smear] = smear_grades

        thin_is_grade3_at_time = 3 in grades_by_smear.get('thin', [])
        thick_is_grade3_at_time = 3 in grades_by_smear.get('thick', [])

        # Check if BOTH thin and thick are Grade 3 at this timestamp
        if thin_is_grade3_at_time and thick_is_grade3_at_time:
            both_smears_optimal_candidates.append(time)
            if verbose:
                print(f"      {time} min: thin=3 [OK], thick=3 [OK] -> BOTH OPTIMAL")

        # Check if at least one smear is Grade 3 at this timestamp (for fallback)
        elif thin_is_grade3_at_time or thick_is_grade3_at_time:
            single_smear_optimal_candidates.append(time)
            if verbose:
                smear_status = []
                if thin_is_grade3_at_time:
                    smear_status.append("thin=3 [OK]")
                if thick_is_grade3_at_time:
                    smear_status.append("thick=3 [OK]")
                print(f"      {time} min: {', '.join(smear_status)} -> SINGLE OPTIMAL (fallback)")
        elif verbose:
            grade_str = ', '.join([f"{s}={list(g)}" for s, g in grades_by_smear.items()])
            print(f"      {time} min: {grade_str}")

    # Decision logic:
    # If both thin and thick have Grade 3 somewhere in the batch, we MUST find a timestamp where both are Grade 3
    # Otherwise, use the fallback (single smear)
    optimal_time = None

    if thin_has_grade3_anywhere and thick_has_grade3_anywhere:
        # Both smear types have Grade 3 somewhere - find where they BOTH have it at the same time
        if both_smears_optimal_candidates:
            optimal_time = min(both_smears_optimal_candidates)
            if verbose:
                print(f"      [OK] Both smears have Grade 3 in batch, using earliest timestamp where BOTH are Grade 3: {optimal_time} min")
        else:
            # This shouldn't happen in a well-formed dataset, but handle it
            if verbose:
                print(f"      [!] WARNING: Both smears have Grade 3 somewhere, but not at the same timestamp")
            # Still use fallback
            if single_smear_optimal_candidates:
                optimal_time = min(single_smear_optimal_candidates)
                if verbose:
                    print(f"      [FALLBACK] Using earliest timestamp with at least one Grade 3: {optimal_time} min")
    else:
        # Only one smear type has Grade 3 (or batch only has one smear type) - use fallback
        if single_smear_optimal_candidates:
            optimal_time = min(single_smear_optimal_candidates)
            if verbose:
                print(f"      [FALLBACK] Only one smear type has Grade 3, using earliest: {optimal_time} min")

    # Apply rounding for 3% dilution to ensure times are in expected range (30-45 min)
    if optimal_time is not None and dilution == '3%':
        if optimal_time < 30:
            if verbose:
                print(f"      [ROUNDING] 3% dilution optimal time {optimal_time} min < 30, rounding to 30 min")
            optimal_time = 30

    return optimal_time


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

    for (batch_id, dilution), batch_df in df.groupby(['batch_id', 'dilution']):
        batch_df = batch_df.sort_values('time_minutes')

        time_range = f"{batch_df['time_minutes'].min()}-{batch_df['time_minutes'].max()}"
        smear_types = sorted(batch_df['smear_type'].unique())

        print(f"{batch_id} ({dilution}, {len(batch_df)} images, {time_range} min, smears: {smear_types})")

        optimal_time = find_optimal_time_both_smears(batch_df, dilution=dilution, verbose=verbose)

        optimal_times[(batch_id, dilution)] = optimal_time

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

    df['optimal_time'] = df.apply(lambda row: optimal_times.get((row['batch_id'], row['dilution'])), axis=1)
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
