# Project Structure

```
anti_malaria_campaign/
│
├── README.md                      # Main project documentation
├── requirements.txt               # Python dependencies
├── train_slide_grading.py        # Main training script (run this to train)
│
├── config/                        # Configuration files
│   └── config.yaml               # Training & model configuration
│
├── data/                         # Dataset directory
│   └── data_04/                  # Student data folder (_04 suffix)
│       ├── raw/                  # Raw unprocessed images
│       ├── processed/            # Organized & renamed images (*.jpg)
│       ├── splits/               # CSV files for train/val/test
│       │   ├── metadata.csv     # All images metadata
│       │   ├── train.csv        # Training split
│       │   ├── val.csv          # Validation split
│       │   └── test.csv         # Test split
│       ├── annotations/          # Annotation files
│       └── unlabeled/            # Images with unknown grades
│
├── scripts/                      # Utility scripts
│   ├── README.md                # Scripts documentation
│   ├── organize_dataset.py      # Standardize raw images
│   ├── create_splits.py         # Create train/val/test splits
│   └── create_metadata.py       # Generate metadata CSV
│
├── notebooks/                    # Jupyter notebooks for analysis
│   ├── comprehensive_data_analysis.ipynb  # Comprehensive data report
│   └── results/                 # Notebook outputs and figures
│
├── src/                         # Source code (ML models & utilities)
│   ├── data/                    # Data loading & preprocessing
│   │   ├── stain_time_dataset.py
│   │   ├── stain_time_transforms.py
│   │   └── stain_time_dataset_organizer.py
│   ├── models/                  # Model architectures
│   │   ├── slide_grade_classifier.py
│   │   └── slide_grade_trainer.py
│   ├── evaluation/              # Evaluation & optimization
│   │   └── staining_time_optimizer.py
│   └── utils/                   # Utility functions
│       ├── stain_time_config.py
│       ├── stain_time_logger.py
│       └── stain_time_seed.py
│
├── backend/                     # FastAPI backend server
│   ├── main.py                 # API endpoints
│   ├── requirements.txt        # Backend dependencies
│   └── README.md               # Backend documentation
│
├── frontend/                    # Next.js web interface
│   ├── src/                    # React components
│   ├── package.json            # Node dependencies
│   └── README.md               # Frontend documentation
│
├── checkpoints/                 # Model checkpoints directory
│   └── checkpoints_04/         # Student checkpoints (_04 suffix)
│       └── best_model.pth      # Best model (created after training)
│
├── models/                      # Final trained models directory
│   └── models_04/              # Student models (_04 suffix)
│       └── (model files saved here)
│
├── logs/                        # Training logs directory
│   └── logs_04/                # Student logs (_04 suffix)
│       └── (log files)
│
├── results/                     # Outputs & visualizations directory
│   └── results_04/             # Student results (_04 suffix)
│       ├── figures/            # Generated plots
│       └── reports/            # Analysis reports
│
├── runs/                        # TensorBoard runs directory
│   └── runs_04/                # Student runs (_04 suffix)
│
└── venv/                        # Python virtual environment
```

## Quick Reference

### Key Files to Run:

1. **Train the model:**
   ```bash
   python train_slide_grading.py --config config/config.yaml
   ```

2. **Create data splits:**
   ```bash
   python scripts/create_splits.py
   ```

3. **Organize raw images:**
   ```bash
   python scripts/organize_dataset.py --input_dir data/data_04/raw --output_dir data/data_04/processed --execute
   ```

4. **Analyze dataset:**
   - Open `notebooks/comprehensive_data_analysis.ipynb` in Jupyter

### Important Folders:

- **`data/data_04/processed/`** - Your labeled training images
- **`checkpoints/checkpoints_04/`** - Saved model weights during training
- **`config/`** - All hyperparameters and settings
- **`backend/`** - API that uses the trained model
- **`frontend/`** - Web UI for users

### Clean Root Directory:

Only 2 files in root:
- `README.md` - Documentation
- `requirements.txt` - Dependencies
- `train_slide_grading.py` - Main training script

Everything else is properly organized in folders!
