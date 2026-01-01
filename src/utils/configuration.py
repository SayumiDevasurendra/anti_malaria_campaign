"""
Centralized configuration for the AMC Stain Time Optimization project.
"""

from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent


# MODEL PATHS ----

# Main model checkpoint directory (where models are saved/loaded)
MODEL_CHECKPOINT_DIR = PROJECT_ROOT / 'models' / 'models_04' / 'model-01'

# Best model file path (used for inference)
BEST_MODEL_PATH = MODEL_CHECKPOINT_DIR / 'best_model.pth'


# DATA PATHS ----

# Data directory
DATA_DIR = PROJECT_ROOT / 'data' / 'data_04'

# Training and validation splits
TRAIN_CSV_PATH = DATA_DIR / 'splits' / 'train_optimal.csv'
VAL_CSV_PATH = DATA_DIR / 'splits' / 'val_optimal.csv'


# OUTPUT PATHS ----

# TensorBoard logs
TENSORBOARD_DIR = PROJECT_ROOT / 'runs' / 'runs_04'

# Training logs
LOG_DIR = PROJECT_ROOT / 'logs' / 'logs_04'


# MODEL CONFIGURATION ----

# Model architecture
DEFAULT_ARCHITECTURE = 'resnet18'

# Image size
DEFAULT_IMAGE_SIZE = (512, 512)

# Number of grade classes
NUM_GRADE_CLASSES = 5


# TRAINING CONFIGURATION ----

# Training hyperparameters
DEFAULT_BATCH_SIZE = 16
DEFAULT_NUM_EPOCHS = 50
DEFAULT_LEARNING_RATE = 1e-4

# Multi-task loss weights
DEFAULT_GRADE_WEIGHT = 0.7
DEFAULT_TIME_WEIGHT = 0.3

# Class balancing
DEFAULT_USE_CLASS_WEIGHTS = True
DEFAULT_USE_JOINT_SAMPLER = True

# Device
DEFAULT_DEVICE = 'cuda'

# Random seed
DEFAULT_SEED = 42


# API CONFIGURATION ----

# API settings
API_HOST = "0.0.0.0"
API_PORT = 8000
CORS_ORIGINS = ["http://localhost:3000"]


# INFERENCE CONFIGURATION ----

# Grade classification
PASS_THRESHOLD = 3  # AMC: Only Grade III is acceptable
DEFAULT_CONFIDENCE_THRESHOLD = 0.8
STABILITY_WINDOW = 2


# HELPER FUNCTIONS ----

def get_model_path() -> str:
    """Get the best model path as a string."""
    return str(BEST_MODEL_PATH)


def get_checkpoint_dir() -> str:
    """Get the checkpoint directory as a string."""
    return str(MODEL_CHECKPOINT_DIR)


def get_tensorboard_dir() -> str:
    """Get the TensorBoard directory as a string."""
    return str(TENSORBOARD_DIR)


def get_log_dir() -> str:
    """Get the log directory as a string."""
    return str(LOG_DIR)


def get_train_csv() -> str:
    """Get the training CSV path as a string."""
    return str(TRAIN_CSV_PATH)


def get_val_csv() -> str:
    """Get the validation CSV path as a string."""
    return str(VAL_CSV_PATH)
