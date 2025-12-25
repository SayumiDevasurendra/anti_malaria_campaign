"""
FastAPI Backend for Stain Time Optimization System

Provides API endpoints for the Next.js frontend to communicate with the ML models.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import torch
from PIL import Image
import io
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_classifier import create_slide_grade_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.staining_time_optimizer import StainingTimeOptimizer

app = FastAPI(title="Stain Time Optimization API", version="0.1.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global model cache
MODEL_CACHE = {}
TRANSFORM = get_stain_time_val_transforms((512, 512))


def load_model(model_path: str = "checkpoints_04/best_model.pth"):
    """Load and cache the model"""
    if model_path not in MODEL_CACHE:
        model = create_slide_grade_model(architecture='resnet18', num_grade_classes=5)
        checkpoint = torch.load(model_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        MODEL_CACHE[model_path] = model
    return MODEL_CACHE[model_path]


@app.get("/")
async def root():
    return {"message": "Stain Time Optimization API", "version": "0.1.0"}


@app.post("/api/grade-slide")
async def grade_slide(
    file: UploadFile = File(...),
    dilution: Optional[str] = Form(None),
    smear_type: Optional[str] = Form(None),
    stain_time: Optional[int] = Form(None),
    batch_id: Optional[str] = Form(None)
):
    """
    Grade a single slide image

    Returns:
        - grade_numeric: Grade as number (1-5)
        - grade_label: Grade as Roman numeral (I-V)
        - confidence: Confidence score (0-1)
        - status: PASS or FAIL
        - probabilities: List of probabilities for each grade
    """
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Load model
        model = load_model()

        # Transform and predict
        image_tensor = TRANSFORM(image).unsqueeze(0)

        with torch.no_grad():
            logits = model(image_tensor)
            probs = torch.softmax(logits, dim=1)
            confidence, prediction = torch.max(probs, dim=1)

            grade_numeric = prediction.item() + 1  # Convert 0-4 to 1-5
            grade_label = ['I', 'II', 'III', 'IV', 'V'][prediction.item()]
            confidence_score = confidence.item()

            # AMC: Only Grade III is acceptable
            is_pass = (grade_numeric == 3)

            return {
                "grade_numeric": grade_numeric,
                "grade_label": grade_label,
                "confidence": confidence_score,
                "status": "PASS" if is_pass else "FAIL",
                "probabilities": probs[0].tolist(),
                "metadata": {
                    "dilution": dilution,
                    "smear_type": smear_type,
                    "stain_time": stain_time,
                    "batch_id": batch_id
                }
            }

    except Exception as e:
        return {"error": str(e)}, 500


@app.post("/api/optimal-time")
async def find_optimal_time(
    files: List[UploadFile] = File(...),
    dilution: str = Form(...),
    confidence_threshold: float = Form(0.8)
):
    """
    Analyze minute-by-minute sweep to find optimal staining time

    Returns:
        - status: success or failure
        - optimal_minute: Optimal minute (if found)
        - pass_probability: Pass probability at optimal minute
        - mean_grade: Mean grade at optimal minute
        - message: Status message
        - passing_minutes: List of all passing minutes
        - minute_analyses: Detailed analysis for each minute
    """
    try:
        # Load model
        model = load_model()

        # Initialize optimizer
        optimizer = StainingTimeOptimizer(
            model=model,
            device='cpu',
            pass_threshold=3,  # AMC: Grade III only
            confidence_threshold=confidence_threshold,
            stability_window=2
        )

        minute_analyses = {}

        # Process each file
        for idx, file in enumerate(files):
            # Extract time from form data (passed as separate field)
            # In real implementation, this would come from the form
            minute = 5 + idx  # Default placeholder

            # Read image
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data)).convert('RGB')

            # Transform and predict
            image_tensor = TRANSFORM(image).unsqueeze(0)

            with torch.no_grad():
                logits = model(image_tensor)
                probs = torch.softmax(logits, dim=1)

            # Analyze minute
            grades = (torch.argmax(probs, dim=1) + 1).numpy()
            confidences = torch.max(probs, dim=1)[0].numpy()

            # Pass probability (Grade III only - index 2)
            pass_prob = probs[:, 2].mean().item()

            minute_analyses[minute] = {
                'minute': minute,
                'num_images': 1,
                'predicted_grades': grades.tolist(),
                'mean_grade': float(grades.mean()),
                'std_grade': 0.0,
                'confidences': confidences.tolist(),
                'mean_confidence': float(confidences.mean()),
                'pass_probability': pass_prob,
                'is_pass': pass_prob >= confidence_threshold,
                'grade_distribution': {i+1: int((grades == i+1).sum()) for i in range(5)}
            }

        # Select optimal minute
        result = optimizer.select_optimal_minute(minute_analyses)
        result['minute_analyses'] = minute_analyses

        return result

    except Exception as e:
        return {"error": str(e)}, 500


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "model_loaded": len(MODEL_CACHE) > 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
