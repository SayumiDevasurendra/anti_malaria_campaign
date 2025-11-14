# Stain Time Optimization - Streamlit Application

**Interactive web application for Giemsa staining time optimization**

@author: Sayumi Devasurendra
@version: 0.1.0

---

## Features

### 🎯 Single Slide Grading
- Upload individual slide images
- Get AMC grade (I-V) with confidence
- Pass/fail determination
- Failure diagnosis with corrective actions

### ⏱️ Optimal Time Finder
- Upload minute-by-minute sweep images
- Automated analysis of staining progression
- Recommends earliest acceptable staining time
- Supports 10% (rapid) and 3% (slow) methods

### 📊 Batch Analysis
- Compare optimal times across batches
- Site-level performance tracking
- Trend visualization
- Quality control monitoring

### 📈 Pattern Viewer
- National staining time patterns
- Regional comparisons
- Recommended starting times for new sites

---

## Installation

### 1. Install Dependencies

```bash
# From project root
pip install -r streamlit_app/requirements.txt
```

### 2. Ensure Model is Trained

Make sure you have a trained model checkpoint in `checkpoints/best_model.pth`

```bash
# Train model if needed
python train_slide_grading.py --config config/config.yaml
```

---

## Running the App

### Local Development

```bash
# From project root
streamlit run streamlit_app/app.py
```

The app will open in your browser at `http://localhost:8501`

### Custom Port

```bash
streamlit run streamlit_app/app.py --server.port 8502
```

### Production Deployment

```bash
# With specific configuration
streamlit run streamlit_app/app.py --server.port 80 --server.address 0.0.0.0
```

---

## Directory Structure

```
streamlit_app/
├── app.py                          # Main application entry point
├── pages/
│   ├── 1_🎯_Single_Slide_Grading.py   # Single slide analysis
│   ├── 2_⏱️_Optimal_Time_Finder.py   # Minute-by-minute sweep
│   ├── 3_📊_Batch_Analysis.py        # Batch comparison
│   └── 4_📈_Pattern_Viewer.py        # National patterns
├── components/
│   ├── model_loader.py             # Model loading utilities
│   └── visualizations.py           # Reusable visualizations
├── utils/                          # Helper functions
├── assets/
│   ├── images/                     # Images and logos
│   └── css/                        # Custom CSS
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

---

## Usage Guide

### Single Slide Grading

1. Navigate to **🎯 Single Slide Grading** page
2. Upload a slide image (JPG, PNG, TIF)
3. Optionally enter metadata (dilution, time, etc.)
4. Click **Analyze Slide**
5. View grade, confidence, and pass/fail status
6. Download results as CSV

### Optimal Time Finder

1. Navigate to **⏱️ Optimal Time Finder** page
2. Select dilution method (10% or 3%)
3. Upload images from minute-by-minute sweep
4. Assign staining times to each image
5. Click **Analyze Sweep**
6. View recommended optimal time
7. Download summary report

### Batch Analysis

1. Navigate to **📊 Batch Analysis** page
2. Upload batch data CSV or load sample data
3. Select analysis type (Single/Multi-Batch/Site-Level)
4. Explore visualizations and statistics
5. Download filtered data

### Pattern Viewer

1. Navigate to **📈 Pattern Viewer** page
2. View national staining time patterns
3. Explore regional variations
4. Get recommended starting times for new sites

---

## Configuration

### Model Settings

Edit in sidebar of each page:
- Model checkpoint path
- Confidence thresholds
- Pass/fail criteria

### Custom Styling

Add custom CSS in `assets/css/` and import in `app.py`

---

## Data Formats

### Single Slide
- Upload: JPG, PNG, TIF, TIFF
- Output: CSV with grade, confidence, status

### Optimal Time Finder
- Upload: Multiple images from sweep
- Output: CSV with optimal minute, pass probability

### Batch Analysis
- Input CSV format:
```csv
batch_id,site,dilution,optimal_minute,pass_probability,mean_grade,date
BATCH_001,AMC_HQ,10%,8,0.92,3.4,2025-01-10
```

---

## Troubleshooting

### Port Already in Use

```bash
# Use different port
streamlit run streamlit_app/app.py --server.port 8502
```

### Model Not Found

Ensure model exists at specified path:
```bash
ls checkpoints/best_model.pth
```

Train if needed:
```bash
python train_slide_grading.py --config config/config.yaml
```

### Import Errors

Install all dependencies:
```bash
pip install -r requirements.txt
pip install -r streamlit_app/requirements.txt
```

---

## Deployment Options

### Streamlit Cloud
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy from `streamlit_app/app.py`

### Docker
```dockerfile
FROM python:3.9
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
RUN pip install -r streamlit_app/requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app/app.py"]
```

### Local Server
```bash
# Run in background
nohup streamlit run streamlit_app/app.py &
```

---

## Support

For issues or questions:
- Check this README
- Review Streamlit documentation: https://docs.streamlit.io
- Contact: Sayumi Devasurendra

---

**Component:** Stain Time Optimization
**Author:** Sayumi Devasurendra
**Version:** 0.1.0
