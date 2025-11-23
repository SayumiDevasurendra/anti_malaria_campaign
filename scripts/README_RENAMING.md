# Image Renaming Quick Start Guide

## Problem

Your current image filenames have:
- ❌ Spaces instead of underscores
- ❌ Inconsistent capitalization
- ❌ Extra words ("batch", "BACH", "positive")
- ❌ Missing file extensions

**These will NOT work** with the data loading pipeline!

## Solution

Use the automated renaming script to fix all filenames at once.

---

## Step-by-Step Instructions

### Step 1: Put all your images in a folder

Example:
```
data/raw/
  ├── 10% batch 5 5 min thick smear grade 2
  ├── 3% BACH 7 27 MIN THICK SMEAR GRADE 2
  ├── 10% Batch 1 5 min thick smeargrade 2
  └── ... (more images)
```

⚠️ **Important:** Make sure your images have proper extensions (.jpg, .png, .tif)!

If they don't have extensions, add them manually first.

---

### Step 2: Run the script in DRY RUN mode (preview)

This shows you what will be renamed WITHOUT actually renaming:

```bash
python scripts/rename_images.py --input_dir data/raw --dry_run
```

**Output:**
```
================================================================================
RENAME PLAN
================================================================================

1. 10% batch 5 5 min thick smear grade 2.jpg
   → 10%_batch5_5min_2_thick.jpg
   Metadata: {'dilution': '10%', 'batch': '5', 'time': '5', 'grade': '2', 'smear': 'thick'}

2. 3% BACH 7 27 MIN THICK SMEAR GRADE 2.jpg
   → 3%_batch7_27min_2_thick.jpg
   Metadata: {'dilution': '3%', 'batch': '7', 'time': '27', 'grade': '2', 'smear': 'thick'}

...

Summary: 16 files will be renamed, 0 failed
================================================================================
💡 This was a DRY RUN. No files were renamed.
   To execute renames, run with --execute flag
```

---

### Step 3: Review the rename plan

Check that all files are being renamed correctly. Pay attention to:
- ✅ Dilution is correct (10% or 3%)
- ✅ Batch numbers are correct
- ✅ Times are correct
- ✅ Grades are correct (1-5 or I-V)
- ✅ Smear types are correct (thin or thick)

If something looks wrong, check the original filename and the naming guide.

---

### Step 4: Execute the renames

Once you're happy with the plan, run with `--execute`:

```bash
python scripts/rename_images.py --input_dir data/raw --execute
```

**Output:**
```
🔄 Executing renames...
  ✓ 10% batch 5 5 min thick smear grade 2.jpg → 10%_batch5_5min_2_thick.jpg
  ✓ 3% BACH 7 27 MIN THICK SMEAR GRADE 2.jpg → 3%_batch7_27min_2_thick.jpg
  ...

✅ Renamed 16 files successfully!
📦 Original files backed up to: data/raw/backup_original_names
```

The script automatically creates a backup of your original files in `backup_original_names/` folder!

---

### Step 5: Verify the results

Check your folder:

```
data/raw/
  ├── 10%_batch1_5min_2_thick.jpg  ✅
  ├── 10%_batch2_5min_2_thick.jpg  ✅
  ├── 10%_batch2_17min_4_thick.jpg  ✅
  ├── 3%_batch1_26min_2_thick.jpg  ✅
  └── backup_original_names/
      ├── 10% batch 5 5 min thick smear grade 2.jpg (backup)
      └── ...
```

---

## Command Reference

| Command | Description |
|---------|-------------|
| `--input_dir <path>` | Directory containing images to rename (required) |
| `--dry_run` | Preview renames without executing (safe, default) |
| `--execute` | Actually rename the files |
| `--no_backup` | Skip creating backup (not recommended!) |

### Examples

**Preview renames (safe):**
```bash
python scripts/rename_images.py --input_dir data/raw --dry_run
```

**Execute renames with backup:**
```bash
python scripts/rename_images.py --input_dir data/raw --execute
```

**Execute without backup (not recommended):**
```bash
python scripts/rename_images.py --input_dir data/raw --execute --no_backup
```

---

## Troubleshooting

### "Failed to parse X files"

Some files couldn't be automatically renamed because the script couldn't extract metadata.

**Common reasons:**
1. Missing grade information
2. Unusual spacing or format
3. Typos

**Solution:** Manually rename these files following the guide in `docs/IMAGE_NAMING_GUIDE.md`

### "Permission denied" error

The script can't access the files.

**Solution:**
- Check file permissions
- Close any programs that might have the files open
- Run terminal/command prompt as administrator

### Files don't have extensions

If your files look like this: `10% batch 5 5 min thick smear grade 2` (no .jpg)

**Solution:** Add extensions manually first, then run the script.

On Windows:
```powershell
# In PowerShell
Get-ChildItem data/raw | Where-Object {!$_.Extension} | Rename-Item -NewName {$_.Name + ".jpg"}
```

On Linux/Mac:
```bash
# Add .jpg to all files without extensions
for f in data/raw/*; do
  if [[ ! "$f" =~ \.[a-z]+$ ]]; then
    mv "$f" "$f.jpg"
  fi
done
```

---

## What If Something Goes Wrong?

**Don't worry!** The script creates a backup automatically.

To restore your original files:

1. Delete the renamed files
2. Copy files from `backup_original_names/` back to the main directory

Or just rename the backup folder:
```bash
rm -rf data/raw/*.jpg  # Remove renamed files
mv data/raw/backup_original_names/* data/raw/  # Restore backups
```

---

## After Renaming

Once files are renamed, you can proceed with:

1. **Organize dataset:**
   ```bash
   python scripts/organize_dataset.py --data_dir data/raw --output data/metadata.csv
   ```

2. **Train model:**
   ```bash
   python train.py --config config/config.yaml
   ```

3. **Use Streamlit app:**
   ```bash
   streamlit run streamlit_app/app.py
   ```

---

## Need Help?

- **Naming Guide:** See `docs/IMAGE_NAMING_GUIDE.md` for detailed naming rules
- **Manual Renaming:** If the script fails, use the naming examples in the guide
- **Contact:** Sayumi Devasurendra
