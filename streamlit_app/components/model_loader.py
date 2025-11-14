"""
Model Loading Component

Utilities for loading and caching trained models in Streamlit.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import streamlit as st
import torch
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_classifier import create_slide_grade_model


@st.cache_resource
def load_grade_model(model_path: str, architecture: str = 'resnet18', device: str = 'cpu'):
    """
    Load and cache grade classification model

    Args:
        model_path: Path to model checkpoint
        architecture: Model architecture name
        device: Device to load model on

    Returns:
        Loaded PyTorch model
    """
    try:
        # Check if model file exists
        if not Path(model_path).exists():
            st.error(f"Model checkpoint not found: {model_path}")
            return None

        # Create model
        model = create_slide_grade_model(
            model_type='single_task',
            architecture=architecture,
            num_grade_classes=5,
            pretrained=False  # Don't need pretrained for inference
        )

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=device)

        # Load state dict
        if 'model_state_dict' in checkpoint:
            model.load_state_dict(checkpoint['model_state_dict'])
        else:
            model.load_state_dict(checkpoint)

        # Set to eval mode
        model.eval()
        model.to(device)

        return model

    except Exception as e:
        st.error(f"Error loading model: {str(e)}")
        return None


def get_available_models(checkpoint_dir: str = 'checkpoints') -> list:
    """
    Get list of available model checkpoints

    Args:
        checkpoint_dir: Directory containing model checkpoints

    Returns:
        List of checkpoint file paths
    """
    checkpoint_path = Path(checkpoint_dir)

    if not checkpoint_path.exists():
        return []

    # Find all .pth files
    models = list(checkpoint_path.glob('*.pth'))

    return [str(m) for m in models]
