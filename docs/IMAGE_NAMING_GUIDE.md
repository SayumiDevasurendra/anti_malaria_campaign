# Image Naming Convention Guide

## AMC Malaria Slide Quality Grading - Image Naming Standards

### Required Format

All slide images **must** follow this naming convention:

```
dilution_batchID_timemin_grade_smeartype.ext
```

### Components

| Component | Format | Examples | Notes |
|-----------|--------|----------|-------|
| **dilution** | `10%` or `3%` | `10%`, `3%` | Must include `%` symbol |
| **batchID** | `batch#` | `batch1`, `batch5` | Lowercase "batch" + number (no spaces) |
| **time** | `#min` | `5min`, `27min` | Number + "min" (no spaces) |
| **grade** | Roman or numeric | `I`, `II`, `III`, `IV`, `V` or `1`, `2`, `3`, `4`, `5` | Uppercase for Roman numerals |
| **smeartype** | `thin` or `thick` | `thin`, `thick` | Lowercase only |
| **extension** | `.jpg`, `.png`, `.tif` | `.jpg` | Standard image formats |

### Correct Examples ✅

```
10%_batch1_5min_2_thick.jpg
10%_batch2_17min_4_thick.jpg
10%_batch5_5min_II_thick.jpg
3%_batch1_26min_2_thick.jpg
3%_batch7_27min_II_thick.jpg
3%_batch4_24min_III_thin.jpg
10%_batch1_7min_II_thin.jpg
```

### Incorrect Examples ❌

| Bad Example | Why It's Wrong | Correct Version |
|-------------|----------------|-----------------|
| `10% batch 5 5 min thick smear grade 2` | Spaces instead of underscores | `10%_batch5_5min_2_thick.jpg` |
| `3% BACH 7 27 MIN THICK SMEAR GRADE 2` | Typo, all caps, spaces | `3%_batch7_27min_2_thick.jpg` |
| `positive 3% batch 1 26 min` | Extra prefix, spaces | `3%_batch1_26min_2_thick.jpg` |
| `10% bach 2, 17min grade 4` | Comma, spaces | `10%_batch2_17min_4_thick.jpg` |

### Additional Rules

1. **No spaces** - Use underscores `_` only
2. **Lowercase** for batch, min, thin/thick
3. **Uppercase** for Roman numeral grades (I, II, III, IV, V)
4. **No extra words** - Only the 5 required components
5. **Consistent order** - dilution → batch → time → grade → smear
6. **File extension** - Add proper extension (.jpg, .png, etc.)

### Optional: Simplified Format (Without Batch)

If batch tracking is not needed, you can use:

```
dilution_timemin_grade_smeartype.ext
```

Examples:
```
10%_5min_2_thick.jpg
3%_27min_III_thick.jpg
10%_7min_II_thin.jpg
```

### Malaria Parasite Status (Optional Prefix)

For slides with confirmed malaria parasites, you can optionally add a prefix:

```
positive_dilution_batchID_timemin_grade_smeartype.ext
```

Examples:
```
positive_3%_batch1_26min_2_thick.jpg
positive_3%_batch2_26min_2_thick.jpg
```

**Note:** The parser currently does NOT require or use this prefix. If used, the parsing script will need to strip it.

---

## Quick Reference

### Your Files → Corrected Names

| Your Current Name | Standardized Name |
|-------------------|-------------------|
| `10% batch 5 5 min thick smear grade 2` | `10%_batch5_5min_2_thick.jpg` |
| `3% BACH 7 27 MIN THICK SMEAR GRADE 2` | `3%_batch7_27min_2_thick.jpg` |
| `10% Batch 1 5 min thick smeargrade 2` | `10%_batch1_5min_2_thick.jpg` |
| `10% bach 2, 17min thick smear grade 4` | `10%_batch2_17min_4_thick.jpg` |
| `10%Batch 3 5 min thick smear Grade 2` | `10%_batch3_5min_2_thick.jpg` |
| `10% batch 4 5 min thick smear grade 2` | `10%_batch4_5min_2_thick.jpg` |
| `positive 3% batch 1 26 min thick smear grade 2` | `3%_batch1_26min_2_thick.jpg` |
| `positive 3% batch 2 26 min thick smear grade 2` | `3%_batch2_26min_2_thick.jpg` |
| `10% batch 1 7min thin smear grade 2` | `10%_batch1_7min_2_thin.jpg` |
| `10% batch 2 5 min thick smear grade 2` | `10%_batch2_5min_2_thick.jpg` |
| `3% BATCH 1 27 MIN THICK SMEAR` | `3%_batch1_27min_UNKNOWN_thick.jpg` ⚠️ Missing grade! |
| `3% BATCH 2 27 MIN THICK SMEAR GRADE 4` | `3%_batch2_27min_4_thick.jpg` |
| `3% BATCH 3 27 MIN THICK SMEAR grade 2` | `3%_batch3_27min_2_thick.jpg` |
| `3% BATCH 4 24 MIN THIN SMEAR GRADE 3` | `3%_batch4_24min_3_thin.jpg` |
| `3% BATCH 5 28MIN THICK SMEAR GRADE 2` | `3%_batch5_28min_2_thick.jpg` |
| `3% BATCH 6 27MIN THICK SMEAR GRADE 2` | `3%_batch6_27min_2_thick.jpg` |

---

## Tools

Use the provided `rename_images.py` script to automatically rename all files in a directory.

```bash
python rename_images.py --input_dir data/raw --dry_run
```
