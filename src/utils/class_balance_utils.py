"""
Class balancing utilities for multi-task grade + time model

Provides:
1. Class weight calculation for imbalanced grade distribution
2. Time-delta aware sample weighting
3. Joint sampler considering grade, dilution, and time_delta
4. Analysis functions for understanding class distribution

Author: Sayumi Devasurendra
"""

import torch
import numpy as np
import pandas as pd
from torch.utils.data import WeightedRandomSampler
from typing import Dict, Tuple, Optional, List
from collections import Counter


# ============================================================================
# Grade Class Weight Calculation
# ============================================================================

def calculate_class_weights(
    labels: np.ndarray,
    num_classes: int = 5,
    method: str = 'inverse'
) -> torch.Tensor:
    """
    Calculate class weights for imbalanced classification

    Args:
        labels: Array of class labels (0-indexed, e.g., 0-4 for grades 1-5)
        num_classes: Total number of classes (default: 5 for grades 1-5)
        method: Weighting method ('inverse' or 'effective')

    Returns:
        Tensor of class weights (shape: [num_classes])
    """
    from sklearn.utils.class_weight import compute_class_weight

    unique_classes = np.unique(labels)

    if method == 'inverse':
        # Simple inverse frequency weighting
        class_weights = compute_class_weight(
            'balanced',
            classes=unique_classes,
            y=labels
        )

    elif method == 'effective':
        # Effective number of samples (Cui et al., 2019)
        # Less aggressive weighting for very imbalanced datasets
        beta = 0.9999
        samples_per_class = Counter(labels)

        effective_num = np.zeros(num_classes)
        for cls_idx in range(num_classes):
            n = samples_per_class.get(cls_idx, 0)
            if n > 0:
                effective_num[cls_idx] = (1 - beta ** n) / (1 - beta)
            else:
                effective_num[cls_idx] = 0

        # Inverse of effective number
        weights = np.where(effective_num > 0, 1.0 / effective_num, 0)

        # Normalize
        if weights.sum() > 0:
            weights = weights / weights.sum() * len(unique_classes)

        class_weights = weights

    else:
        raise ValueError(f"Unknown method: {method}")

    # Create full weight tensor (some classes may have 0 samples)
    weight_tensor = torch.zeros(num_classes, dtype=torch.float32)
    for cls, weight in zip(unique_classes, class_weights):
        weight_tensor[cls] = weight

    return weight_tensor


# ============================================================================
# Time Delta Weighting
# ============================================================================

def calculate_time_delta_weights(
    time_deltas: np.ndarray,
    bins: List[float] = None,
    smoothing: float = 0.1
) -> np.ndarray:
    """
    Calculate sample weights based on time_delta distribution

    Ensures model learns to handle both small and large time corrections.

    Args:
        time_deltas: Array of time deltas (optimal_time - current_time)
        bins: Bin edges for grouping time deltas
              Default: [-inf, -5, -2, 0, 2, 5, inf]
        smoothing: Laplace smoothing to avoid zero weights

    Returns:
        Array of sample weights (one per sample)
    """
    if bins is None:
        bins = [-np.inf, -5, -2, 0, 2, 5, np.inf]

    # Assign each sample to a bin
    bin_indices = np.digitize(time_deltas, bins) - 1

    # Count samples per bin
    bin_counts = Counter(bin_indices)
    total_samples = len(time_deltas)

    # Calculate inverse frequency weights with smoothing
    weights = np.zeros(len(time_deltas))
    for i, bin_idx in enumerate(bin_indices):
        bin_count = bin_counts[bin_idx]
        # Inverse frequency with Laplace smoothing
        weights[i] = total_samples / (bin_count + smoothing)

    # Normalize to have mean = 1
    weights = weights / weights.mean()

    return weights


# ============================================================================
# Joint Sampling (Grade + Dilution + Time Delta)
# ============================================================================

def create_weighted_sampler(
    labels: np.ndarray,
    num_classes: int = 5,
    method: str = 'inverse'
) -> WeightedRandomSampler:
    """
    Create a weighted random sampler for balanced batch sampling

    Args:
        labels: Array of class labels (0-indexed)
        num_classes: Total number of classes
        method: Weighting method ('inverse' or 'effective')

    Returns:
        WeightedRandomSampler instance
    """
    # Calculate class weights
    class_weights = calculate_class_weights(labels, num_classes, method)

    # Map to sample weights
    sample_weights = torch.tensor([class_weights[label].item() for label in labels])

    # Create sampler
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )

    return sampler


def create_joint_weighted_sampler(
    df: pd.DataFrame,
    grade_weight: float = 0.5,
    dilution_weight: float = 0.3,
    time_delta_weight: float = 0.2,
    method: str = 'inverse'
) -> WeightedRandomSampler:
    """
    Create sampler considering grade, dilution, AND time_delta

    This ensures batches have:
    - Balanced representation of all grades
    - Both 10% and 3% dilutions
    - Diverse time_delta values

    Args:
        df: DataFrame with columns 'grade_numeric', 'dilution', 'time_delta'
        grade_weight: Weight for grade balancing (default: 0.5)
        dilution_weight: Weight for dilution balancing (default: 0.3)
        time_delta_weight: Weight for time_delta balancing (default: 0.2)
        method: Weighting method for grade weights

    Returns:
        WeightedRandomSampler instance
    """
    # 1. Grade weights
    grades = df['grade_numeric'].values - 1  # Convert to 0-indexed
    grade_class_weights = calculate_class_weights(grades, num_classes=5, method=method)
    grade_sample_weights = np.array([grade_class_weights[g].item() for g in grades])

    # 2. Dilution weights
    dilutions = df['dilution'].values
    dilution_counts = Counter(dilutions)
    total_samples = len(dilutions)
    dilution_weights_map = {dil: total_samples / count for dil, count in dilution_counts.items()}
    dilution_sample_weights = np.array([dilution_weights_map[d] for d in dilutions])

    # 3. Time delta weights
    time_deltas = df['time_delta'].values
    time_delta_sample_weights = calculate_time_delta_weights(time_deltas)

    # Combine weights (weighted average)
    combined_weights = (
        grade_weight * grade_sample_weights +
        dilution_weight * dilution_sample_weights +
        time_delta_weight * time_delta_sample_weights
    )

    # Normalize
    combined_weights = combined_weights / combined_weights.mean()

    # Create sampler
    sampler = WeightedRandomSampler(
        weights=torch.tensor(combined_weights, dtype=torch.float32),
        num_samples=len(combined_weights),
        replacement=True
    )

    return sampler


# ============================================================================
# Class Distribution Analysis
# ============================================================================

def analyze_class_distribution(df: pd.DataFrame) -> Dict:
    """
    Analyze class distribution in dataset

    Args:
        df: DataFrame with 'grade_numeric' column

    Returns:
        Dictionary with distribution statistics
    """
    grade_counts = df['grade_numeric'].value_counts().sort_index()
    total = len(df)

    # Calculate percentages
    percentages = {grade: (count / total) * 100 for grade, count in grade_counts.items()}

    # Imbalance metrics
    max_count = grade_counts.max()
    min_count = grade_counts.min()
    imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

    # Balance ratio (0 = completely imbalanced, 1 = perfectly balanced)
    balance_ratio = min_count / max_count if max_count > 0 else 0

    return {
        'total_samples': total,
        'num_classes': len(grade_counts),
        'distribution': dict(grade_counts),
        'percentages': percentages,
        'max_class': grade_counts.idxmax(),
        'max_count': max_count,
        'min_class': grade_counts.idxmin(),
        'min_count': min_count,
        'imbalance_ratio': imbalance_ratio,
        'balance_ratio': balance_ratio
    }


def analyze_time_delta_distribution(df: pd.DataFrame) -> Dict:
    """
    Analyze time_delta distribution

    Args:
        df: DataFrame with 'time_delta' column

    Returns:
        Dictionary with time delta statistics
    """
    time_deltas = df['time_delta'].values

    # Basic statistics
    stats = {
        'mean': float(np.mean(time_deltas)),
        'median': float(np.median(time_deltas)),
        'std': float(np.std(time_deltas)),
        'min': float(np.min(time_deltas)),
        'max': float(np.max(time_deltas)),
        'range': float(np.ptp(time_deltas))
    }

    # Categorization
    at_optimal = np.sum(time_deltas == 0)
    before_optimal = np.sum(time_deltas > 0)
    after_optimal = np.sum(time_deltas < 0)

    stats['at_optimal_count'] = int(at_optimal)
    stats['before_optimal_count'] = int(before_optimal)
    stats['after_optimal_count'] = int(after_optimal)
    stats['at_optimal_pct'] = float(at_optimal / len(time_deltas) * 100)
    stats['before_optimal_pct'] = float(before_optimal / len(time_deltas) * 100)
    stats['after_optimal_pct'] = float(after_optimal / len(time_deltas) * 100)

    return stats


def analyze_dilution_distribution(df: pd.DataFrame) -> Dict:
    """
    Analyze dilution distribution

    Args:
        df: DataFrame with 'dilution' column

    Returns:
        Dictionary with dilution statistics
    """
    if 'dilution' not in df.columns:
        return {'error': 'No dilution column found'}

    dilution_counts = df['dilution'].value_counts()
    total = len(df)

    stats = {
        'total_samples': total,
        'dilution_types': list(dilution_counts.index),
        'distribution': dict(dilution_counts),
        'percentages': {dil: (count / total) * 100 for dil, count in dilution_counts.items()}
    }

    return stats


def print_class_distribution(stats: Dict, title: str = "Class Distribution"):
    """
    Pretty print class distribution statistics

    Args:
        stats: Dictionary from analyze_class_distribution()
        title: Title for the report
    """
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(f"Total samples: {stats['total_samples']}")
    print(f"Number of classes: {stats['num_classes']}")
    print(f"\nDistribution:")

    for grade in sorted(stats['distribution'].keys()):
        count = stats['distribution'][grade]
        pct = stats['percentages'][grade]
        bar_length = int(pct / 2)  # Scale for terminal display
        bar = '█' * bar_length
        print(f"  Grade {grade}: {count:3d} ({pct:5.2f}%) {bar}")

    print(f"\nImbalance Metrics:")
    print(f"  Most common: Grade {stats['max_class']} ({stats['max_count']} samples)")
    print(f"  Least common: Grade {stats['min_class']} ({stats['min_count']} samples)")
    print(f"  Imbalance ratio: {stats['imbalance_ratio']:.2f}x")
    print(f"  Balance ratio: {stats['balance_ratio']:.2f} (0=imbalanced, 1=balanced)")
    print("=" * 60)


def print_time_delta_distribution(stats: Dict, title: str = "Time Delta Distribution"):
    """
    Pretty print time delta distribution statistics

    Args:
        stats: Dictionary from analyze_time_delta_distribution()
        title: Title for the report
    """
    print("=" * 60)
    print(title)
    print("=" * 60)
    print(f"Mean: {stats['mean']:+.2f} minutes")
    print(f"Median: {stats['median']:+.2f} minutes")
    print(f"Std Dev: {stats['std']:.2f} minutes")
    print(f"Range: [{stats['min']:+.1f}, {stats['max']:+.1f}] minutes")

    print(f"\nTiming Categories:")
    print(f"  At optimal (Δ=0):    {stats['at_optimal_count']:3d} ({stats['at_optimal_pct']:.1f}%)")
    print(f"  Before optimal (Δ>0): {stats['before_optimal_count']:3d} ({stats['before_optimal_pct']:.1f}%) - Understained")
    print(f"  After optimal (Δ<0):  {stats['after_optimal_count']:3d} ({stats['after_optimal_pct']:.1f}%) - Overstained")
    print("=" * 60)


# ============================================================================
# Test/Demo
# ============================================================================

if __name__ == '__main__':
    # Demo with synthetic data
    print("Class Balance Utils - Demo\n")

    # Simulate imbalanced grade data
    np.random.seed(42)
    grades = np.concatenate([
        np.full(100, 0),  # Grade 1: 100 samples
        np.full(80, 1),   # Grade 2: 80 samples
        np.full(50, 2),   # Grade 3: 50 samples (minority)
        np.full(150, 3),  # Grade 4: 150 samples (majority)
        np.full(60, 4),   # Grade 5: 60 samples
    ])

    # Calculate weights
    weights_inv = calculate_class_weights(grades, num_classes=5, method='inverse')
    weights_eff = calculate_class_weights(grades, num_classes=5, method='effective')

    print("Grade Class Weights:")
    print("-" * 40)
    for i in range(5):
        print(f"  Grade {i+1}: {weights_inv[i]:.4f} (inverse), {weights_eff[i]:.4f} (effective)")

    # Simulate time deltas
    time_deltas = np.random.randn(len(grades)) * 4 - 2  # Mean=-2, std=4
    time_weights = calculate_time_delta_weights(time_deltas)

    print(f"\n\nTime Delta Weights:")
    print("-" * 40)
    print(f"  Mean weight: {time_weights.mean():.4f}")
    print(f"  Std weight: {time_weights.std():.4f}")
    print(f"  Range: [{time_weights.min():.4f}, {time_weights.max():.4f}]")

    # Create sample DataFrame
    df = pd.DataFrame({
        'grade_numeric': grades + 1,  # Convert back to 1-5
        'time_delta': time_deltas,
        'dilution': np.random.choice(['10%', '3%'], size=len(grades))
    })

    # Analyze distribution
    grade_stats = analyze_class_distribution(df)
    print_class_distribution(grade_stats, "\nGrade Distribution Analysis")

    time_stats = analyze_time_delta_distribution(df)
    print_time_delta_distribution(time_stats, "\nTime Delta Distribution Analysis")

    print("\n✓ Demo complete!")
