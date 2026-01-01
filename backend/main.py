"""
Provides API endpoints for the Next.js frontend to communicate with the ML models.
"""

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import torch
from PIL import Image
import io
import sys
from pathlib import Path
import numpy as np
import base64

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Define model path relative to project root
DEFAULT_MODEL_PATH = str(project_root / 'outputs' / 'checkpoints_grade_time_balanced' / 'best_model.pth')

from models.slide_grade_time_recommender import create_grade_time_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.staining_time_optimizer import StainingTimeOptimizer
from evaluation.gradcam_explainer import GradeExplainer

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
EXPLAINER_CACHE = {}
FINDER_CACHE = {}
TRANSFORM = get_stain_time_val_transforms((512, 512))


def load_model(model_path: str = None):
    """Load and cache the multi-task model (grade + time)"""
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    if model_path not in MODEL_CACHE:
        model = create_grade_time_model(
            architecture='resnet18',
            num_grade_classes=5,
            pretrained=False,  # Will be loaded from checkpoint
            use_time_context=True
        )
        checkpoint = torch.load(model_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        model.eval()
        MODEL_CACHE[model_path] = model
    return MODEL_CACHE[model_path]


def load_explainer(model_path: str = None, device: str = 'cpu'):
    """Load and cache the Grad-CAM explainer"""
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    cache_key = f"{model_path}_{device}"
    if cache_key not in EXPLAINER_CACHE:
        model = load_model(model_path)
        explainer = GradeExplainer(model, device=device)
        EXPLAINER_CACHE[cache_key] = explainer
    return EXPLAINER_CACHE[cache_key]


@app.get("/")
async def root():
    return {"message": "Stain Time Optimization API", "version": "0.1.0"}


@app.post("/api/grade-slide")
async def grade_slide(
    file: UploadFile = File(...),
    dilution: Optional[str] = Form(None),
    smear_type: Optional[str] = Form(None),
    stain_time: Optional[int] = Form(None)
):
    """Simple grading without time recommendation"""
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Load model
        model = load_model()

        # Transform and predict
        image_tensor = TRANSFORM(image).unsqueeze(0)
        current_time_tensor = torch.tensor([stain_time or 0], dtype=torch.float32)

        with torch.no_grad():
            # Multi-task model returns (grade_logits, time_deltas)
            output = model(image_tensor, current_time_tensor)

            # Handle multi-task model
            if isinstance(output, tuple):
                logits, _ = output  # Ignore time_deltas for simple grading
            else:
                logits = output

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
                    "stain_time": stain_time
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
    """Batch analysis: minute-by-minute sweep for optimal staining time"""
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
                output = model(image_tensor)

                # Handle multi-task model
                if isinstance(output, tuple):
                    logits, _ = output  # Ignore time_deltas
                else:
                    logits = output

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
        import traceback
        print(f"Error in grade_slide: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e), "details": traceback.format_exc()}


@app.post("/api/explain-grade")
async def explain_grade(
    file: UploadFile = File(...),
    dilution: str = Form(...),
    smear_type: str = Form(...),
    stain_time: float = Form(...),
    return_overlay_base64: bool = Form(True)
):
    """Tab 1: Diagnostic with Grad-CAM explanation"""
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Convert to numpy for Grad-CAM
        image_np = np.array(image)

        # Load explainer
        explainer = load_explainer(device='cpu')

        # Transform image
        image_tensor = TRANSFORM(image).unsqueeze(0)

        # Prepare current_time tensor from user input
        current_time_tensor = torch.tensor([stain_time], dtype=torch.float32)

        # Generate explanation
        explanation = explainer.explain(image_tensor, image_np, current_time_tensor)

        # Prepare response
        response = {
            "grade_numeric": explanation['grade_numeric'],
            "grade_label": explanation['grade_label'],
            "confidence": explanation['confidence'],
            "status": explanation['status'],
            "reason": explanation['reason'],
            "probabilities": explanation['probabilities'],
            "metadata": {
                "dilution": dilution,
                "smear_type": smear_type,
                "stain_time": stain_time
            }
        }

        # Add overlay image as base64 if requested
        if return_overlay_base64:
            # Convert overlay to base64
            overlay_pil = Image.fromarray(explanation['overlay_image'])
            buffer = io.BytesIO()
            overlay_pil.save(buffer, format='PNG')
            buffer.seek(0)
            overlay_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            response['overlay_image_base64'] = overlay_base64

        return response

    except Exception as e:
        import traceback
        print(f"Error in explain_grade: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e), "details": traceback.format_exc()}


@app.post("/api/recommend-time")
async def recommend_time(
    file: UploadFile = File(...),
    current_time: float = Form(...),
    dilution: str = Form(...),
    smear_type: str = Form(...)
):
    """Tab 2: Optimal time finder with time recommendations"""
    try:
        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert('RGB')

        # Load model
        model = load_model()

        # Transform image
        image_tensor = TRANSFORM(image).unsqueeze(0)
        current_time_tensor = torch.tensor([current_time], dtype=torch.float32)

        with torch.no_grad():
            # Multi-task model returns (grade_logits, time_deltas)
            grade_logits, time_deltas = model(image_tensor, current_time_tensor)

            # Grade prediction
            probs = torch.softmax(grade_logits, dim=1)
            confidence, prediction = torch.max(probs, dim=1)

            grade_numeric = prediction.item() + 1  # Convert 0-4 to 1-5
            grade_label = ['I', 'II', 'III', 'IV', 'V'][prediction.item()]
            confidence_score = confidence.item()

            # Time recommendation
            time_delta = time_deltas.item()
            recommended_time = current_time + time_delta

            # Status: OPTIMAL if Grade III, else NOT_OPTIMAL
            is_optimal = (grade_numeric == 3)
            status = "OPTIMAL" if is_optimal else "NOT_OPTIMAL"

            # Generate recommendation message
            if is_optimal:
                recommendation_message = (
                    f"✅ Optimal staining time found! "
                    f"The slide at {current_time:.0f} minutes shows Grade III (Optimal). "
                    f"Document this as the optimal staining time for your batch "
                    f"({dilution} dilution, {smear_type} smear)."
                )
                reason = "Slide achieved optimal staining quality (Grade III)."
            else:
                # Round to reasonable time range
                recommended_min = int(recommended_time)
                recommended_max = recommended_min + 2

                if grade_numeric <= 2:  # Under-stained
                    recommendation_message = (
                        f"⏱️ Slide is under-stained (Grade {grade_label}). "
                        f"Try staining at {recommended_min}-{recommended_max} minutes "
                        f"(+{time_delta:+.1f} min adjustment from current {current_time:.0f} min)."
                    )
                    reason = f"Under-stained. Additional staining time needed to reach Grade III."
                else:  # Over-stained (Grade IV or V)
                    recommendation_message = (
                        f"⏱️ Slide is over-stained (Grade {grade_label}). "
                        f"Try staining at {recommended_min}-{recommended_max} minutes "
                        f"({time_delta:+.1f} min adjustment from current {current_time:.0f} min)."
                    )
                    reason = f"Over-stained. Reduce staining time to reach Grade III."

            return {
                "grade_numeric": grade_numeric,
                "grade_label": grade_label,
                "confidence": confidence_score,
                "status": status,
                "time_delta": round(time_delta, 2),
                "recommended_time": round(recommended_time, 1),
                "recommendation_message": recommendation_message,
                "reason": reason,
                "probabilities": probs[0].tolist(),
                "metadata": {
                    "current_time": current_time,
                    "dilution": dilution,
                    "smear_type": smear_type
                }
            }

    except Exception as e:
        import traceback
        print(f"Error in recommend_time: {str(e)}")
        print(traceback.format_exc())
        return {"error": str(e), "details": traceback.format_exc()}


@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": len(MODEL_CACHE) > 0,
        "explainer_loaded": len(EXPLAINER_CACHE) > 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
