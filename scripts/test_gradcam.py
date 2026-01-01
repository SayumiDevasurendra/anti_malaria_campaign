"""
Test Grad-CAM explainer for visualizing grade predictions
Usage: python scripts/test_gradcam.py
"""

import argparse
import sys
from pathlib import Path
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_time_recommender import create_grade_time_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.gradcam_explainer import GradeExplainer
from utils.configuration import (
    get_model_path,
    DEFAULT_IMAGE_SIZE,
    NUM_GRADE_CLASSES,
    DEFAULT_ARCHITECTURE,
    PROJECT_ROOT
)

# Test image path
DEFAULT_TEST_IMAGE = project_root / 'data' / 'data_04' / 'processed' / 'batch01_10%_10min_3_thin.jpg'

# Stain time for the test image (in minutes) - change this based on the test image
DEFAULT_STAIN_TIME = 10.0  # 10 minutes for the default test image

# Output path for visualization
DEFAULT_OUTPUT_PATH = project_root / 'results' / 'results_04' / 'figures' / 'gradcam' / 'gradcam_output.png'

# Device selection (auto-detects GPU, falls back to CPU)
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

def main():
    parser = argparse.ArgumentParser(
        description='Test Grad-CAM Explainer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Default Configuration:
  Image:      {DEFAULT_TEST_IMAGE}
  Stain Time: {DEFAULT_STAIN_TIME} minutes
  Model:      {get_model_path()}
  Output:     {DEFAULT_OUTPUT_PATH}
  Device:     {DEVICE}

Can override any of these by passing CLI arguments.
        """
    )
    parser.add_argument('--image', type=str, default=str(DEFAULT_TEST_IMAGE),
                        help=f'Path to input image (default: {DEFAULT_TEST_IMAGE.name})')
    parser.add_argument('--stain-time', type=float, default=DEFAULT_STAIN_TIME,
                        help=f'Staining time in minutes (default: {DEFAULT_STAIN_TIME})')
    parser.add_argument('--model', type=str, default=get_model_path(),
                        help='Path to trained model checkpoint')
    parser.add_argument('--output', type=str, default=str(DEFAULT_OUTPUT_PATH),
                        help='Path to save visualization')
    parser.add_argument('--device', type=str, default=DEVICE,
                        choices=['cuda', 'cpu'],
                        help=f'Device to use (default: auto-detected as {DEVICE})')
    args = parser.parse_args()

    device = args.device
    if device == 'cuda' and not torch.cuda.is_available():
        print("⚠ CUDA requested but not available, using CPU")
        device = 'cpu'
    elif device == 'cpu' and torch.cuda.is_available():
        print("ℹ CPU selected (GPU available but not being used)")

    print("=" * 60)
    print("GRAD-CAM SLIDE GRADE EXPLAINER")
    print("=" * 60)
    print(f"Image: {args.image}")
    print(f"Stain Time: {args.stain_time} minutes")
    print(f"Model: {args.model}")
    print(f"Device: {device}")
    print()

    print("Loading model...")
    model = create_grade_time_model(
        architecture=DEFAULT_ARCHITECTURE,
        num_grade_classes=NUM_GRADE_CLASSES,
        pretrained=False,
        use_time_context=True
    )
    checkpoint = torch.load(args.model, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("✓ Model loaded (dual-head: grade + time)")

    print(f"Loading image: {args.image}")
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        return

    image = Image.open(image_path).convert('RGB')
    image_np = np.array(image)
    print(f"✓ Image loaded (size: {image.size})")

    transform = get_stain_time_val_transforms(DEFAULT_IMAGE_SIZE)
    image_tensor = transform(image).unsqueeze(0)

    # Prepare stain time tensor
    stain_time_tensor = torch.tensor([args.stain_time], dtype=torch.float32)

    print("\nInitializing Grad-CAM explainer...")
    explainer = GradeExplainer(model, device=device)
    print("✓ Explainer initialized")

    print("\nGenerating explanation...")
    explanation = explainer.explain(image_tensor, image_np, stain_time_tensor)

    print("\n" + "=" * 60)
    print("PREDICTION RESULTS")
    print("=" * 60)
    print(f"Grade: {explanation['grade_label']} ({explanation['grade_numeric']})")
    print(f"Status: {explanation['status']}")
    print(f"Confidence: {explanation['confidence']:.2%}")
    print(f"Reason: {explanation['reason']}")
    print()
    print("Class Probabilities:")
    for i, prob in enumerate(explanation['probabilities']):
        grade_label = ['I', 'II', 'III', 'IV', 'V'][i]
        bar = '█' * int(prob * 50)
        print(f"  Grade {grade_label}: {prob:.2%} {bar}")
    print("=" * 60)

    print(f"\nGenerating visualization...")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    axes[0].imshow(image_np)
    axes[0].set_title('Original Image', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    axes[1].imshow(explanation['cam_heatmap'], cmap='jet')
    axes[1].set_title('Grad-CAM Heatmap\n(Attention Map)', fontsize=14, fontweight='bold')
    axes[1].axis('off')

    axes[2].imshow(explanation['overlay_image'])
    axes[2].set_title(
        f"Grade {explanation['grade_label']}: {explanation['reason']}\n"
        f"Confidence: {explanation['confidence']:.2%}",
        fontsize=14, fontweight='bold',
        color='green' if explanation['status'] == 'PASS' else 'red'
    )
    axes[2].axis('off')

    plt.tight_layout()

    # Ensure output directory exists and create unique filename
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate unique filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = Path(args.image).stem  # Get image filename without extension
    unique_filename = f"gradcam_{image_name}_{timestamp}.png"
    final_output_path = output_path.parent / unique_filename

    plt.savefig(final_output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Visualization saved to: {final_output_path}")

    try:
        plt.show()
    except:
        print("(Display not available, saved to file only)")

    print("\n" + "=" * 60)
    print("GRAD-CAM EXPLANATION COMPLETE!")
    print("=" * 60)


if __name__ == '__main__':
    main()
