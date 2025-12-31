@echo off
REM Training script with recommended class balancing settings (Windows)
REM
REM Usage:
REM   scripts\train_balanced.bat

REM Set paths
set TRAIN_CSV=data\data_04\splits\train_optimal.csv
set VAL_CSV=data\data_04\splits\val_optimal.csv
set CHECKPOINT_DIR=checkpoints_grade_time_balanced
set TENSORBOARD_DIR=runs/runs_04

REM Training parameters
set ARCHITECTURE=resnet18
set IMG_SIZE=512
set BATCH_SIZE=16
set EPOCHS=50
set LR=0.0001
set GRADE_WEIGHT=0.7
set TIME_WEIGHT=0.3

echo ==========================================
echo Training Grade + Time Model (Balanced)
echo ==========================================
echo.
echo Dataset:
echo   Train: %TRAIN_CSV%
echo   Val: %VAL_CSV%
echo.
echo Model Settings:
echo   Architecture: %ARCHITECTURE%
echo   Image Size: %IMG_SIZE%x%IMG_SIZE%
echo   Batch Size: %BATCH_SIZE%
echo   Epochs: %EPOCHS%
echo   Learning Rate: %LR%
echo.
echo Balancing Strategy:
echo   + Class weights in loss (inverse frequency)
echo   + Joint weighted sampler (grade + dilution + time_delta)
echo   + Loss weights: %GRADE_WEIGHT% (grade) + %TIME_WEIGHT% (time)
echo.
echo ==========================================
echo.

REM Run training
python main_pipeline\train_grade_time_model.py ^
    --train-csv %TRAIN_CSV% ^
    --val-csv %VAL_CSV% ^
    --checkpoint-dir %CHECKPOINT_DIR% ^
    --tensorboard-dir %TENSORBOARD_DIR% ^
    --architecture %ARCHITECTURE% ^
    --img-size %IMG_SIZE% ^
    --batch-size %BATCH_SIZE% ^
    --epochs %EPOCHS% ^
    --lr %LR% ^
    --grade-weight %GRADE_WEIGHT% ^
    --time-weight %TIME_WEIGHT% ^
    --device cuda ^
    --seed 42

echo.
echo ==========================================
echo Training Complete!
echo Checkpoints saved to: %CHECKPOINT_DIR%
echo ==========================================

pause
