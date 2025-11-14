"""
Stain Time Data Setup Script

Organizes Giemsa-stained slide images for stain time optimization:
1. Scans and parses slide images from raw directory
2. Extracts metadata from filenames (dilution, time, grade, smear type)
3. Creates stratified train/validation/test splits
4. Generates dataset statistics and visualizations

@author: Sayumi Devasurendra
@version: 0.1.0

Usage:
    python setup_stain_time_data.py --data_dir "data/raw"
"""

import argparse
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.stain_time_dataset_organizer import StainTimeDatasetOrganizer
from utils.stain_time_config import StainTimeConfig
from utils.stain_time_logger import setup_stain_time_logger


def visualize_dataset(df: pd.DataFrame, output_dir: str = 'results/figures'):
    """Create visualizations of dataset statistics"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)

    # 1. Grade distribution
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Overall grade distribution
    grade_counts = df['grade_label'].value_counts().sort_index()
    axes[0, 0].bar(grade_counts.index, grade_counts.values, color='steelblue')
    axes[0, 0].set_title('Overall Grade Distribution', fontsize=14, fontweight='bold')
    axes[0, 0].set_xlabel('Grade')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].grid(axis='y', alpha=0.3)

    # Grade by dilution
    grade_by_dilution = df.groupby(['dilution', 'grade_label']).size().unstack(fill_value=0)
    grade_by_dilution.plot(kind='bar', ax=axes[0, 1], color=sns.color_palette("Set2"))
    axes[0, 1].set_title('Grade Distribution by Dilution', fontsize=14, fontweight='bold')
    axes[0, 1].set_xlabel('Dilution')
    axes[0, 1].set_ylabel('Count')
    axes[0, 1].legend(title='Grade')
    axes[0, 1].grid(axis='y', alpha=0.3)

    # Staining time distribution
    for dilution in df['dilution'].unique():
        subset = df[df['dilution'] == dilution]
        axes[1, 0].hist(subset['time_minutes'], bins=20, alpha=0.6, label=dilution)
    axes[1, 0].set_title('Staining Time Distribution', fontsize=14, fontweight='bold')
    axes[1, 0].set_xlabel('Time (minutes)')
    axes[1, 0].set_ylabel('Count')
    axes[1, 0].legend()
    axes[1, 0].grid(axis='y', alpha=0.3)

    # Smear type distribution
    smear_counts = df['smear_type'].value_counts()
    axes[1, 1].pie(smear_counts.values, labels=smear_counts.index, autopct='%1.1f%%',
                    colors=sns.color_palette("pastel"))
    axes[1, 1].set_title('Smear Type Distribution', fontsize=14, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path / 'dataset_overview.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization: {output_path / 'dataset_overview.png'}")
    plt.close()

    # 2. Time vs Grade heatmap
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    for idx, dilution in enumerate(sorted(df['dilution'].unique())):
        subset = df[df['dilution'] == dilution]

        # Create pivot table for heatmap
        pivot = subset.pivot_table(
            index='grade_label',
            columns='time_minutes',
            values='filename',
            aggfunc='count',
            fill_value=0
        )

        sns.heatmap(pivot, annot=True, fmt='g', cmap='YlOrRd', ax=axes[idx], cbar_kws={'label': 'Count'})
        axes[idx].set_title(f'Grade vs Time - {dilution} Dilution', fontsize=14, fontweight='bold')
        axes[idx].set_xlabel('Time (minutes)')
        axes[idx].set_ylabel('Grade')

    plt.tight_layout()
    plt.savefig(output_path / 'grade_time_heatmap.png', dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization: {output_path / 'grade_time_heatmap.png'}")
    plt.close()


def print_statistics(organizer: DatasetOrganizer, df: pd.DataFrame):
    """Print detailed dataset statistics"""
    stats = organizer.get_dataset_statistics(df)

    print("\n" + "=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)

    print(f"\nTotal Images: {stats['total_images']}")

    print("\nDilutions:")
    for dilution, count in stats['dilutions'].items():
        print(f"  {dilution}: {count} images")

    print("\nGrades:")
    for grade, count in sorted(stats['grades'].items()):
        print(f"  Grade {grade}: {count} images")

    print("\nSmear Types:")
    for smear_type, count in stats['smear_types'].items():
        print(f"  {smear_type}: {count} images")

    print("\nTime Ranges:")
    for dilution, info in stats['time_range'].items():
        print(f"  {dilution}: {info['min']}-{info['max']} minutes ({info['count']} images)")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description='AMC Malaria Slide Quality Grading - Starter Script')
    parser.add_argument('--data_dir', type=str, default='data/raw',
                        help='Directory containing slide images')
    parser.add_argument('--output_dir', type=str, default='data/processed',
                        help='Directory for processed metadata')
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    args = parser.parse_args()

    # Setup logger
    logger = setup_stain_time_logger(name='SlideQuality_Setup', log_dir='logs')
    logger.info("Starting slide quality grading dataset setup...")

    # Load configuration
    try:
        config = StainTimeConfig(args.config)
        logger.info(f"✓ Loaded configuration from {args.config}")
    except Exception as e:
        logger.warning(f"Could not load config: {e}. Using defaults.")
        config = None

    print("\n" + "=" * 60)
    print("SLIDE QUALITY GRADING - DATASET SETUP")
    print("=" * 60)

    # Step 1: Organize dataset
    print("\n[Step 1/5] Organizing dataset...")
    print(f"Data directory: {args.data_dir}")

    if not Path(args.data_dir).exists():
        logger.error(f"Data directory not found: {args.data_dir}")
        print(f"\n❌ Error: Directory '{args.data_dir}' does not exist!")
        print("\nPlease:")
        print(f"  1. Create the directory: mkdir -p {args.data_dir}")
        print(f"  2. Place your slide images in {args.data_dir}")
        print(f"  3. Run this script again")
        return

    organizer = StainTimeDatasetOrganizer(args.data_dir)

    # Scan and parse images
    output_csv = Path(args.output_dir) / 'metadata.csv'
    df = organizer.organize_dataset(output_csv=str(output_csv))

    if len(df) == 0:
        logger.error("No images found or parsed successfully!")
        print("\n❌ Error: No valid images found!")
        print("\nPlease check that:")
        print("  1. Your images are in the correct directory")
        print("  2. Filenames follow the expected pattern (e.g., '10%_8min_III_thin.jpg')")
        print("\nSupported patterns:")
        print("  - dilution_time_grade_smear.ext (e.g., 10%_8min_III_thin.jpg)")
        print("  - dilution_time_grade.ext (e.g., 3%_35min_IV.jpg)")
        return

    # Step 2: Print statistics
    print("\n[Step 2/5] Computing statistics...")
    print_statistics(organizer, df)

    # Step 3: Create visualizations
    print("\n[Step 3/5] Creating visualizations...")
    try:
        visualize_dataset(df, output_dir='results/figures')
    except Exception as e:
        logger.warning(f"Visualization failed: {e}")
        print(f"⚠ Warning: Could not create visualizations: {e}")

    # Step 4: Create train/val/test splits
    print("\n[Step 4/5] Creating train/val/test splits...")

    # Get split ratios from config or use defaults
    if config:
        train_ratio = config.get('data.split_ratios.train', 0.7)
        val_ratio = config.get('data.split_ratios.val', 0.15)
        test_ratio = config.get('data.split_ratios.test', 0.15)
        random_seed = config.get('data.random_seed', 42)
    else:
        train_ratio, val_ratio, test_ratio = 0.7, 0.15, 0.15
        random_seed = 42

    try:
        train_df, val_df, test_df = organizer.create_train_val_test_split(
            df,
            train_ratio=train_ratio,
            val_ratio=val_ratio,
            test_ratio=test_ratio,
            random_state=random_seed
        )

        # Save splits
        output_dir = Path(args.output_dir)
        train_df.to_csv(output_dir / 'train.csv', index=False)
        val_df.to_csv(output_dir / 'val.csv', index=False)
        test_df.to_csv(output_dir / 'test.csv', index=False)

        print(f"\n✓ Saved splits to {output_dir}/")

    except Exception as e:
        logger.error(f"Failed to create splits: {e}")
        print(f"❌ Error creating splits: {e}")

    # Step 5: Next steps
    print("\n[Step 5/5] Setup complete!")
    print("\n" + "=" * 60)
    print("NEXT STEPS")
    print("=" * 60)

    print("\n1. Review your data:")
    print(f"   - Metadata: {output_csv}")
    print(f"   - Visualizations: results/figures/")
    print(f"   - Splits: {args.output_dir}/train.csv, val.csv, test.csv")

    print("\n2. Train the slide grading model:")
    print("   python train_slide_grading.py --config config/config.yaml")

    print("\n3. Use trained model for staining time optimization:")
    print("   (See staining_time_optimizer.py module)")

    print("\n" + "=" * 60)

    logger.info("Project setup complete!")


if __name__ == '__main__':
    main()
