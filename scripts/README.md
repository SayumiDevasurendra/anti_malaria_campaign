# Scripts Directory

This folder contains utility scripts for data preparation and organization.

## Available Scripts

### 1. `stain_time_dataset_organizer.py`
**Purpose:** Standardize and rename raw slide images
**Usage:**
```bash
python scripts/stain_time_dataset_organizer.py --input_dir data/data_04/raw --output_dir data/data_04/processed --execute
```
**What it does:**
- Scans raw images recursively
- Parses metadata from filenames (dilution, batch, time, grade, smear type)
- Renames to standard format: `{dilution}_batch{batch}_{time}min_{grade}_{smear}.jpg`
- Flattens all images to single output directory

---

### 2. `stain_time_split_generator.py`
**Purpose:** Create train/validation/test splits from processed images
**Usage:**
```bash
python scripts/stain_time_split_generator.py
```
**What it does:**
- Scans processed images
- Creates stratified splits (70% train, 15% val, 15% test)
- Generates CSV files: `metadata.csv`, `train.csv`, `val.csv`, `test.csv`
- Ensures grade distribution is balanced across splits

---

### 3. `stain_time_metadata_generator.py`
**Purpose:** Generate metadata CSV from organized images
**Usage:**
```bash
python scripts/stain_time_metadata_generator.py
```
**What it does:**
- Scans processed images
- Extracts metadata from filenames
- Saves to `data/data_04/splits/metadata.csv`

---

## Typical Workflow

1. **Organize raw data:**
   ```bash
   python scripts/stain_time_dataset_organizer.py --input_dir data/data_04/raw --output_dir data/data_04/processed --execute
   ```

2. **Create train/val/test splits:**
   ```bash
   python scripts/stain_time_split_generator.py
   ```

3. **Deep analysis (optional):**
   Open and run `notebooks/comprehensive_data_analysis.ipynb`

4. **Train model:**
   ```bash
   python train_slide_grading_balanced --config config/config.yaml
   ```
