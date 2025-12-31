#!/bin/bash
# Training script with recommended class balancing settings
#
# Usage:
#   bash scripts/train_balanced.sh
#
# Or on Windows:
#   bash scripts/train_balanced.sh
#   (or use train_balanced.bat)

# Set paths
TRAIN_CSV="data/data_04/splits/train_optimal.csv"
VAL_CSV="data/data_04/splits/val_optimal.csv"
CHECKPOINT_DIR="checkpoints_grade_time_balanced"
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
python main_pipeline/train_grade_time_model.py \
    --train-csv "$TRAIN_CSV" \
    --val-csv "$VAL_CSV" \
    --checkpoint-dir "$CHECKPOINT_DIR" \
    --tensorboard-dir "$TENSORBOARD_DIR" \
    --architecture "$ARCHITECTURE" \
    --img-size "$IMG_SIZE" \
    --batch-size "$BATCH_SIZE" \
    --epochs "$EPOCHS" \
    --lr "$LR" \
    --grade-weight "$GRADE_WEIGHT" \
    --time-weight "$TIME_WEIGHT" \
    --device cuda \
    --seed 42

echo ""
echo "=========================================="
echo "Training Complete!"
echo "Checkpoints saved to: $CHECKPOINT_DIR"
echo "=========================================="
