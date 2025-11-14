"""
Stain Time Reproducibility Module

Random seed management for reproducible experiments.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import random
import numpy as np
import torch


def set_stain_time_seed(seed: int = 42, deterministic: bool = True, benchmark: bool = False):
    """
    Set random seeds for reproducibility

    Args:
        seed: Random seed value
        deterministic: Use deterministic algorithms (slower but reproducible)
        benchmark: Enable cudnn benchmark (faster but less reproducible)
    """
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    else:
        torch.backends.cudnn.benchmark = benchmark

    # Set environment variables for additional reproducibility
    import os
    os.environ['PYTHONHASHSEED'] = str(seed)
