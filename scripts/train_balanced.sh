#!/bin/bash
# Training script with recommended class balancing settings
#
# Usage:
#   bash scripts/train_balanced.sh
#
# Or on Windows:
#   bash scripts/train_balanced.sh
#   (or use train_balanced.bat)
#
# NOTE: Paths are now configured in src/utils/configuration.py
#       To change model paths, edit that file instead of this script.
#       These variables are kept here only for display purposes.

# Set paths (for display only - actual defaults come from configuration.py)
TRAIN_CSV="data/data_04/splits/train_optimal.csv"
VAL_CSV="data/data_04/splits/val_optimal.csv"
CHECKPOINT_DIR="models/models_04/model-01"
TENSORBOARD_DIR="runs/runs_04"

# Training parameters
ARCHITECTURE="resnet18"
IMG_SIZE=512
BATCH_SIZE=16
EPOCHS=50
LR=0.0001
GRADE_WEIGHT=0.7
TIME_WEIGHT=0.3

# Balancing parameters (enabled by default)
# Add --no-class-weights to disable class weights
# Add --no-joint-sampler to use simple grade sampler

echo "=========================================="
echo "Training Grade + Time Model (Balanced)"
echo "=========================================="
echo ""
echo "Dataset:"
echo "  Train: $TRAIN_CSV"
echo "  Val: $VAL_CSV"
echo ""
echo "Model Settings:"
echo "  Architecture: $ARCHITECTURE"
echo "  Image Size: ${IMG_SIZE}x${IMG_SIZE}"
echo "  Batch Size: $BATCH_SIZE"
echo "  Epochs: $EPOCHS"
echo "  Learning Rate: $LR"
echo ""
echo "Balancing Strategy:"
echo "  ✓ Class weights in loss (inverse frequency)"
echo "  ✓ Joint weighted sampler (grade + dilution + time_delta)"
echo "  ✓ Loss weights: ${GRADE_WEIGHT} (grade) + ${TIME_WEIGHT} (time)"
echo ""
echo "=========================================="
echo ""

# Run training
# Note: Most parameters now use defaults from src/utils/configuration.py
# Only specify parameters here if you want to override the defaults
python main_pipeline/train_grade_time_model.py \
    --train-csv "$TRAIN_CSV" \
    --val-csv "$VAL_CSV"

echo ""
echo "=========================================="
echo "Training Complete!"
echo "Checkpoints saved to: $CHECKPOINT_DIR"
echo "=========================================="
