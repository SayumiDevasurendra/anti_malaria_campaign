# Scripts Directory

This folder contains utility scripts for data preparation and organization.

## Available Scripts

### 1. `organize_dataset.py`
**Purpose:** Standardize and rename raw slide images
**Usage:**
```bash
python scripts/organize_dataset.py --input_dir data/data_04/raw --output_dir data/data_04/processed --execute
```
**What it does:**
- Scans raw images recursively
- Parses metadata from filenames (dilution, batch, time, grade, smear type)
- Renames to standard format: `{dilution}_batch{batch}_{time}min_{grade}_{smear}.jpg`
- Flattens all images to single output directory

---

### 2. `create_splits.py`
**Purpose:** Create train/validation/test splits from processed images
**Usage:**
```bash
python scripts/create_splits.py
```
**What it does:**
- Scans processed images
- Creates stratified splits (70% train, 15% val, 15% test)
- Generates CSV files: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`
- Ensures grade distribution is balanced across splits

---

### 3. `create_metadata.py`
**Purpose:** Generate metadata CSV from organized images
**Usage:**
```bash
python scripts/create_metadata.py
```
**What it does:**
- Scans processed images
- Extracts metadata from filenames
- Saves to `data/data_04/splits/metadata.csv`

---

## Typical Workflow

1. **Organize raw data:**
   ```bash
   python scripts/organize_dataset.py --input_dir data/data_04/raw --output_dir data/data_04/processed --execute
   ```

2. **Create train/val/test splits:**
   ```bash
   python scripts/create_splits.py
   ```

3. **Deep analysis (optional):**
   Open and run `notebooks/comprehensive_data_analysis.ipynb`

4. **Train model:**
   ```bash
   python train_slide_grading.py --config config/config.yaml
   ```
