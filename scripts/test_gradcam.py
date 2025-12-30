"""Test Grad-CAM explainer for visualizing grade predictions"""

import argparse
import sys
from pathlib import Path
import torch
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_classifier import create_slide_grade_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.gradcam_explainer import GradeExplainer


def main():
    parser = argparse.ArgumentParser(description='Test Grad-CAM Explainer')
    parser.add_argument('--image', type=str, required=True,
                        help='Path to input image')
    parser.add_argument('--model', type=str,
                        default='checkpoints/checkpoints_04/best_model.pth',
                        help='Path to trained model checkpoint')
    parser.add_argument('--output', type=str, default='gradcam_output.png',
                        help='Path to save visualization')
    parser.add_argument('--device', type=str, default='cuda',
                        choices=['cuda', 'cpu'],
                        help='Device to use')
    args = parser.parse_args()

    device = args.device
    if device == 'cuda' and not torch.cuda.is_available():
        print("CUDA not available, using CPU")
        device = 'cpu'

    print("=" * 60)
    print("GRAD-CAM SLIDE GRADE EXPLAINER")
    print("=" * 60)
    print(f"Image: {args.image}")
    print(f"Model: {args.model}")
    print(f"Device: {device}")
    print()

    print("Loading model...")
    model = create_slide_grade_model(architecture='resnet18', num_grade_classes=5)
    checkpoint = torch.load(args.model, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    print("✓ Model loaded")

    print(f"Loading image: {args.image}")
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found at {image_path}")
        return

    image = Image.open(image_path).convert('RGB')
    image_np = np.array(image)
    print(f"✓ Image loaded (size: {image.size})")

    transform = get_stain_time_val_transforms((512, 512))
    image_tensor = transform(image).unsqueeze(0)

    print("\nInitializing Grad-CAM explainer...")
    explainer = GradeExplainer(model, device=device)
    print("✓ Explainer initialized")

    print("\nGenerating explanation...")
    explanation = explainer.explain(image_tensor, image_np)

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
    plt.savefig(args.output, dpi=300, bbox_inches='tight')
    print(f"✓ Visualization saved to: {args.output}")

    try:
        plt.show()
    except:
        print("(Display not available, saved to file only)")

    print("\n" + "=" * 60)
    print("GRAD-CAM EXPLANATION COMPLETE!")
    print("=" * 60)


if __name__ == '__main__':
    main()
