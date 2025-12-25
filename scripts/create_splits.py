"""
Simple script to create metadata CSV and train/val/test splits from processed images
"""
import os
import re
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

# Configuration
DATA_DIR = Path("data/data_04/processed")
OUTPUT_DIR = Path("data/data_04/splits")
TRAIN_RATIO = 0.7
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42

print("="*60)
print("CREATING DATASET SPLITS")
print("="*60)

# Scan images
print(f"\nScanning images in: {DATA_DIR}")
image_files = list(DATA_DIR.glob("*.jpg"))
print(f"Found {len(image_files)} images")

# Parse filenames
data = []
for img_path in image_files:
    filename = img_path.name

    # Pattern: dilution_batch#_time_grade_smear.jpg
    # Example: 10%_batch1_10min_3_thick.jpg
    match = re.match(r'(\d+%)_batch(\d+)_(\d+)min_(\d+)_(thick|thin)\.jpg', filename)

    if match:
        dilution, batch, time_min, grade, smear_type = match.groups()

        data.append({
            'filename': str(img_path),
            'dilution': dilution,
            'batch': int(batch),
            'time_minutes': int(time_min),
            'grade_label': grade,
            'grade_numeric': int(grade),
            'smear_type': smear_type
        })
    else:
        print(f"Warning: Could not parse {filename}")

# Create DataFrame
df = pd.DataFrame(data)
print(f"\nSuccessfully parsed {len(df)} images")

# Print statistics
print("\n" + "="*60)
print("DATASET STATISTICS")
print("="*60)
print(f"\nTotal images: {len(df)}")
print(f"\nDilutions:")
for dilution, count in df['dilution'].value_counts().items():
    print(f"  {dilution}: {count}")
print(f"\nGrades:")
for grade in sorted(df['grade_numeric'].unique()):
    count = len(df[df['grade_numeric'] == grade])
    print(f"  Grade {grade}: {count}")
print(f"\nSmear types:")
for smear, count in df['smear_type'].value_counts().items():
    print(f"  {smear}: {count}")

# Create train/val/test splits (stratified by grade)
print("\n" + "="*60)
print("CREATING SPLITS")
print("="*60)

# First split: train vs (val + test)
train_df, temp_df = train_test_split(
    df,
    test_size=(VAL_RATIO + TEST_RATIO),
    stratify=df['grade_numeric'],
    random_state=RANDOM_SEED
)

# Second split: val vs test
val_ratio_adjusted = VAL_RATIO / (VAL_RATIO + TEST_RATIO)
val_df, test_df = train_test_split(
    temp_df,
    test_size=(1 - val_ratio_adjusted),
    stratify=temp_df['grade_numeric'],
    random_state=RANDOM_SEED
)

print(f"\nTrain set: {len(train_df)} images ({len(train_df)/len(df)*100:.1f}%)")
print(f"Val set:   {len(val_df)} images ({len(val_df)/len(df)*100:.1f}%)")
print(f"Test set:  {len(test_df)} images ({len(test_df)/len(df)*100:.1f}%)")

# Save splits
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

metadata_csv = OUTPUT_DIR / 'metadata.csv'
train_csv = OUTPUT_DIR / 'train.csv'
val_csv = OUTPUT_DIR / 'val.csv'
test_csv = OUTPUT_DIR / 'test.csv'

df.to_csv(metadata_csv, index=False)
train_df.to_csv(train_csv, index=False)
val_df.to_csv(val_csv, index=False)
test_df.to_csv(test_csv, index=False)

print(f"\nSaved:")
print(f"  {metadata_csv}")
print(f"  {train_csv}")
print(f"  {val_csv}")
print(f"  {test_csv}")

print("\n" + "="*60)
print("DONE! Ready to train.")
print("="*60)
print("\nNext step:")
print("  python train_slide_grading.py --config config/config.yaml")
