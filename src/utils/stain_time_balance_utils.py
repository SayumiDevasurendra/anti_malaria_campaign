"""
Class imbalance utilities: class weights, weighted sampler, distribution analysis
"""

import numpy as np
import torch
from typing import Dict, List, Tuple
from collections import Counter
import pandas as pd


def calculate_class_weights(labels: np.ndarray, num_classes: int = 5, method: str = 'inverse') -> torch.Tensor:
    """Calculate class weights for imbalanced dataset using 'inverse' or 'effective' method"""
    # Count samples per class
    class_counts = Counter(labels)

    # Initialize weights array
    weights = np.zeros(num_classes)

    if method == 'inverse':
        # Inverse frequency: weight_i = total_samples / (num_classes * count_i)
        total_samples = len(labels)
        for class_idx in range(num_classes):
            count = class_counts.get(class_idx, 0)
            if count > 0:
                weights[class_idx] = total_samples / (num_classes * count)
            else:
                # For missing classes (like Grade 1), assign zero weight
                weights[class_idx] = 0.0

    elif method == 'effective':
        # Effective number of samples (better for extreme imbalance)
        # weight_i = (1 - beta) / (1 - beta^n_i)
        # where beta = (N - 1) / N
        total_samples = len(labels)
        beta = (total_samples - 1) / total_samples

        for class_idx in range(num_classes):
            count = class_counts.get(class_idx, 0)
            if count > 0:
                effective_num = (1 - beta ** count) / (1 - beta)
                weights[class_idx] = 1.0 / effective_num
            else:
                weights[class_idx] = 0.0

        # Normalize weights
        if weights.sum() > 0:
            weights = weights / weights.sum() * num_classes

    else:
        raise ValueError(f"Unknown method: {method}")

    return torch.FloatTensor(weights)


def create_weighted_sampler(labels: np.ndarray, num_classes: int = 5) -> torch.utils.data.WeightedRandomSampler:
    """Create WeightedRandomSampler for balanced batch sampling"""
    # Calculate sample weights (inverse frequency)
    class_counts = Counter(labels)

    # Weight for each sample = 1 / count_of_its_class
    sample_weights = np.zeros(len(labels))
    for idx, label in enumerate(labels):
        count = class_counts[label]
        sample_weights[idx] = 1.0 / count

    # Create sampler
    sampler = torch.utils.data.WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    return sampler


def analyze_class_distribution(df: pd.DataFrame, label_column: str = 'grade_numeric') -> Dict:
    """Analyze class distribution and calculate imbalance metrics"""
    # Get label distribution
    distribution = df[label_column].value_counts().sort_index()

    total_samples = len(df)
    num_classes = len(distribution)

    # Calculate imbalance metrics
    max_count = distribution.max()
    min_count = distribution.min()

    # Imbalance ratio: max_count / min_count
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

    # Balance ratio: min_count / max_count (0 = completely imbalanced, 1 = balanced)
    balance_ratio = min_count / max_count if max_count > 0 else 0.0

    # Calculate percentages
    percentages = (distribution / total_samples * 100).round(2)

    # Prepare statistics
    stats = {
        'total_samples': total_samples,
        'num_classes': num_classes,
        'distribution': distribution.to_dict(),
        'percentages': percentages.to_dict(),
        'imbalance_ratio': round(imbalance_ratio, 2),
        'balance_ratio': round(balance_ratio, 2),
        'max_class': distribution.idxmax(),
        'max_count': int(max_count),
        'min_class': distribution.idxmin(),
        'min_count': int(min_count)
    }

    return stats


def print_class_distribution(stats: Dict, title: str = "Class Distribution"):
    """Print formatted class distribution statistics"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)
    print(f"Total samples: {stats['total_samples']}")
    print(f"Number of classes: {stats['num_classes']}")
    print(f"\nDistribution:")

    for grade, count in sorted(stats['distribution'].items()):
        percentage = stats['percentages'][grade]
        bar_length = int(percentage / 2)  # Scale for display
        bar = "█" * bar_length
        print(f"  Grade {grade}: {count:3d} ({percentage:5.2f}%) {bar}")

    print(f"\nImbalance Metrics:")
    print(f"  Most common: Grade {stats['max_class']} ({stats['max_count']} samples)")
    print(f"  Least common: Grade {stats['min_class']} ({stats['min_count']} samples)")
    print(f"  Imbalance ratio: {stats['imbalance_ratio']:.2f}x")
    print(f"  Balance ratio: {stats['balance_ratio']:.2f} (0=imbalanced, 1=balanced)")
    print("=" * 60)


def get_sample_weights_per_class(df: pd.DataFrame, label_column: str = 'grade_numeric') -> np.ndarray:
    """Get sample weight for each instance based on its class (useful for weighted loss)"""
    labels = df[label_column].values
    class_counts = Counter(labels)

    # Calculate weight for each sample
    sample_weights = np.array([1.0 / class_counts[label] for label in labels])

    # Normalize to sum to number of samples
    sample_weights = sample_weights / sample_weights.mean()

    return sample_weights


if __name__ == '__main__':
    # Example usage
    print("Class Balance Utilities - Example Usage")

    # Simulate imbalanced dataset (similar to actual distribution)
    labels = np.array([1] * 124 + [2] * 81 + [3] * 183 + [4] * 79)

    print("\nSimulated Distribution:")
    print(f"Grade 2 (1): 124 samples")
    print(f"Grade 3 (2): 81 samples")
    print(f"Grade 4 (3): 183 samples")
    print(f"Grade 5 (4): 79 samples")

    # Calculate class weights
    print("\n" + "=" * 60)
    print("Class Weights (Inverse Frequency)")
    print("=" * 60)
    weights_inverse = calculate_class_weights(labels, num_classes=5, method='inverse')
    for i, w in enumerate(weights_inverse):
        if i == 0:
            print(f"Grade 1 (index {i}): {w:.4f} (no data)")
        else:
            print(f"Grade {i+1} (index {i}): {w:.4f}")

    print("\n" + "=" * 60)
    print("Class Weights (Effective Number)")
    print("=" * 60)
    weights_effective = calculate_class_weights(labels, num_classes=5, method='effective')
    for i, w in enumerate(weights_effective):
        if i == 0:
            print(f"Grade 1 (index {i}): {w:.4f} (no data)")
        else:
            print(f"Grade {i+1} (index {i}): {w:.4f}")
