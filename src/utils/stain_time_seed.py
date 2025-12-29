"""
Random seed management for reproducible experiments
"""

import random
import numpy as np
import torch


def set_stain_time_seed(seed: int = 42, deterministic: bool = True, benchmark: bool = False):
    """Set random seeds for reproducibility"""
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
