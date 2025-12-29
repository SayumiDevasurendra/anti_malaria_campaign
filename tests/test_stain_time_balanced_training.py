"""
Test script for balanced training components
Usage: python tests/test_stain_time_balanced_training.py
"""

import sys
from pathlib import Path
import pandas as pd
import torch

sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("=" * 70)
print("TESTING BALANCED TRAINING COMPONENTS")
print("=" * 70)

# Test 1: Import all modules
print("\n[1/6] Testing imports...")
try:
    from utils.stain_time_balance_utils import (
        calculate_class_weights,
        create_weighted_sampler,
        analyze_class_distribution,
        print_class_distribution
    )
    from data.stain_time_balanced_dataset import BalancedStainTimeDataset
    from data.stain_time_dataset import StainTimeDataset
    from data.stain_time_transforms import (
        get_stain_time_train_transforms,
        get_stain_time_val_transforms,
        get_aggressive_augmentation_transforms
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Load dataset
print("\n[2/6] Testing dataset loading...")
try:
    splits_dir = Path('data/data_04/splits')
    train_df = pd.read_csv(splits_dir / 'train.csv')
    print(f"✓ Loaded {len(train_df)} training samples")
except Exception as e:
    print(f"✗ Dataset loading failed: {e}")
    sys.exit(1)

# Test 3: Analyze distribution
print("\n[3/6] Testing distribution analysis...")
try:
    stats = analyze_class_distribution(train_df)
    print_class_distribution(stats, "Training Set Distribution")
    print("✓ Distribution analysis successful")
except Exception as e:
    print(f"✗ Distribution analysis failed: {e}")
    sys.exit(1)

# Test 4: Calculate class weights
print("\n[4/6] Testing class weight calculation...")
try:
    train_labels = train_df['grade_numeric'].values - 1  # 0-indexed
    weights = calculate_class_weights(train_labels, num_classes=5, method='inverse')
    print("Class weights:")
    for i, w in enumerate(weights):
        print(f"  Grade {i+1} (index {i}): {w:.4f}")
    print("✓ Class weight calculation successful")
except Exception as e:
    print(f"✗ Class weight calculation failed: {e}")
    sys.exit(1)

# Test 5: Create weighted sampler
print("\n[5/6] Testing weighted sampler...")
try:
    sampler = create_weighted_sampler(train_labels, num_classes=5)
    print(f"✓ Created weighted sampler with {len(train_labels)} samples")
except Exception as e:
    print(f"✗ Weighted sampler creation failed: {e}")
    sys.exit(1)

# Test 6: Create balanced dataset
print("\n[6/6] Testing balanced dataset creation...")
try:
    image_size = (512, 512)
    base_transform = get_stain_time_train_transforms(image_size)
    minority_transform = get_aggressive_augmentation_transforms(image_size)

    dataset = BalancedStainTimeDataset(
        train_df,
        base_transform=base_transform,
        minority_transform=minority_transform,
        minority_classes=None  # Auto-detect
    )
    print(f"✓ Created balanced dataset with {len(dataset)} samples")

    # Test loading one sample
    sample_img, sample_label = dataset[0]
    print(f"✓ Successfully loaded sample: shape={sample_img.shape}, label={sample_label}")

except Exception as e:
    print(f"✗ Balanced dataset creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# All tests passed
print("\n" + "=" * 70)
print("ALL TESTS PASSED! ✓")
print("=" * 70)
print("\nYou're ready to train with balanced approach:")
print("  python main_pipeline/train_slide_grading_balanced.py")
print("\nNote: Config and balance method use smart defaults (config.yaml, hybrid)")
print("\nTo run this test again:")
print("  python tests/test_stain_time_balanced_training.py")
print("=" * 70)
