@echo off
REM Training script with recommended class balancing settings (Windows)
REM
REM Usage:
REM   scripts\train_balanced.bat
REM
REM NOTE: Paths are now configured in src\utils\configuration.py
REM       To change model paths, edit that file instead of this script.
REM       These variables are kept here only for display purposes.

REM Set paths (for display only - actual defaults come from configuration.py)
set TRAIN_CSV=data\data_04\splits\train_optimal.csv
set VAL_CSV=data\data_04\splits\val_optimal.csv
set CHECKPOINT_DIR=models\models_04\model-01
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
REM Note: All parameters now use defaults from src\utils\configuration.py
REM Only specify parameters here if you want to override the defaults
REM CSV paths are also now configured in src\utils\configuration.py
python main_pipeline\train_grade_time_model.py

echo.
echo ==========================================
echo Training Complete!
echo Checkpoints saved to: %CHECKPOINT_DIR%
echo ==========================================

pause
