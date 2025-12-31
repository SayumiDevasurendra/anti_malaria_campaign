# Stain Time Optimization Backend

FastAPI backend for the AMC Stain Time Optimization System.

## Features

- RESTful API endpoints for slide grading
- Model loading and caching
- Integration with PyTorch models
- CORS support for frontend communication

## Setup

### Prerequisites

- Python 3.8+
- PyTorch
- Trained model checkpoint in `checkpoints/best_model.pth`

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
# Development
python main.py

# Or using uvicorn
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## API Endpoints

### Grade Single Slide

```
POST /api/grade-slide
Content-Type: multipart/form-data

Body:
- file: Image file (JPG, PNG, TIF)
- dilution: "10%" or "3%" (optional)
- smear_type: "thin" or "thick" (optional)
- stain_time: Integer (optional)
- batch_id: String (optional)

Response:
{
  "grade_numeric": 3,
  "grade_label": "III",
  "confidence": 0.92,
  "status": "PASS",
  "probabilities": [0.02, 0.05, 0.92, 0.01, 0.00]
}
```

### Find Optimal Time

```
POST /api/optimal-time
Content-Type: multipart/form-data

Body:
- files: Multiple image files
- dilution: "10%" or "3%"
- confidence_threshold: Float (0.5-1.0)

Response:
{
  "status": "success",
  "optimal_minute": 8,
  "pass_probability": 0.92,
  "mean_grade": 3.4,
  "message": "Optimal time found",
  "passing_minutes": [7, 8, 9],
  "minute_analyses": {...}
}
```

### Health Check

```
GET /api/health

Response:
{
  "status": "healthy",
  "model_loaded": true
}
```

## Model Integration

The backend expects:
- PyTorch model checkpoint at `checkpoints/checkpoints_04/best_model.pth`
- Model architecture: ResNet18 with 5 grade classes
- Input image size: 512x512

## Author

Sayumi Devasurendra
Version: 0.1.0
