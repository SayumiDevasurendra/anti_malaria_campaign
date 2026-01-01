"""Grad-CAM explainer for slide grade classifier

Provides visual explanations for model predictions by highlighting
which regions of the slide image contributed to the grade classification.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Optional, Tuple, Dict
from PIL import Image
import cv2


class GradCAM:
    """Grad-CAM: Gradient-weighted Class Activation Mapping"""

    def __init__(self, model: nn.Module, target_layer: Optional[nn.Module] = None):
        """Initialize Grad-CAM

        Args:
            model: Trained PyTorch model
            target_layer: Layer to generate CAM from (default: last conv layer)
        """
        self.model = model
        self.model.eval()

        # Find target layer if not provided
        if target_layer is None:
            self.target_layer = self._find_target_layer()
        else:
            self.target_layer = target_layer

        # Storage for gradients and activations
        self.gradients = None
        self.activations = None

        # Register hooks
        self._register_hooks()

    def _find_target_layer(self) -> nn.Module:
        """Automatically find the last convolutional layer"""
        # For ResNet architectures
        if hasattr(self.model, 'backbone'):
            # Our custom model structure
            backbone = self.model.backbone

            # For ResNet in Sequential wrapper
            if isinstance(backbone, nn.Sequential):
                # Last layer before avgpool
                for layer in reversed(list(backbone.children())):
                    if isinstance(layer, nn.Sequential):
                        # Get last layer from this Sequential
                        for sublayer in reversed(list(layer.children())):
                            if len(list(sublayer.children())) > 0:
                                # This is a bottleneck/basic block
                                return sublayer
                        return layer

        # Fallback: search all modules
        target = None
        for module in self.model.modules():
            if isinstance(module, (nn.Conv2d, nn.BatchNorm2d)):
                target = module

        if target is None:
            raise ValueError("Could not find target layer automatically. Please specify target_layer.")

        return target

    def _register_hooks(self):
        """Register forward and backward hooks"""
        def forward_hook(module, input, output):
            self.activations = output.detach()

        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()

        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)

    def generate_cam(
        self,
        input_tensor: torch.Tensor,
        target_class: Optional[int] = None,
        current_time: Optional[torch.Tensor] = None
    ) -> np.ndarray:
        """Generate Grad-CAM heatmap

        Args:
            input_tensor: Input image tensor (1, C, H, W)
            target_class: Target class index (if None, uses predicted class)
            current_time: Current staining time (optional, for time-aware models)

        Returns:
            Heatmap as numpy array (H, W) with values in [0, 1]
        """
        # Forward pass
        self.model.zero_grad()

        # current_time is required for time-aware models
        if current_time is None:
            raise ValueError("current_time parameter is required for time-aware models")

        output = self.model(input_tensor, current_time)

        # Handle multi-task model (returns tuple: grade_logits, time_deltas)
        if isinstance(output, tuple):
            output = output[0]  # Use only grade logits for GradCAM

        # Get target class
        if target_class is None:
            target_class = output.argmax(dim=1).item()

        # Backward pass
        self.model.zero_grad()
        class_score = output[0, target_class]
        class_score.backward()

        # Get gradients and activations
        gradients = self.gradients  # (1, C, H, W)
        activations = self.activations  # (1, C, H, W)

        # Calculate weights (global average pooling of gradients)
        weights = gradients.mean(dim=(2, 3), keepdim=True)  # (1, C, 1, 1)

        # Weighted combination of activation maps
        cam = (weights * activations).sum(dim=1, keepdim=True)  # (1, 1, H, W)

        # Apply ReLU (only positive contributions)
        cam = F.relu(cam)

        # Normalize to [0, 1]
        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        return cam

    def generate_overlay(
        self,
        input_image: np.ndarray,
        cam: np.ndarray,
        colormap: int = cv2.COLORMAP_JET,
        alpha: float = 0.4
    ) -> np.ndarray:
        """Create overlay of Grad-CAM heatmap on original image

        Args:
            input_image: Original image as numpy array (H, W, 3) in RGB
            cam: Grad-CAM heatmap (H', W') with values in [0, 1]
            colormap: OpenCV colormap to use
            alpha: Transparency of heatmap overlay (0=transparent, 1=opaque)

        Returns:
            Overlay image as numpy array (H, W, 3) in RGB
        """
        # Resize CAM to match input image size
        h, w = input_image.shape[:2]
        cam_resized = cv2.resize(cam, (w, h))

        # Convert CAM to heatmap
        heatmap = cv2.applyColorMap(np.uint8(255 * cam_resized), colormap)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

        # Ensure input_image is uint8
        if input_image.dtype != np.uint8:
            input_image = np.uint8(input_image)

        # Overlay heatmap on original image
        overlay = cv2.addWeighted(input_image, 1 - alpha, heatmap, alpha, 0)

        return overlay

    def explain_prediction(
        self,
        input_tensor: torch.Tensor,
        input_image: np.ndarray,
        target_class: Optional[int] = None,
        return_prediction: bool = True,
        current_time: Optional[torch.Tensor] = None
    ) -> Dict:
        """Generate full explanation for a prediction

        Args:
            input_tensor: Preprocessed input tensor (1, C, H, W)
            input_image: Original image as numpy array (H, W, 3) in RGB
            target_class: Target class to explain (if None, uses prediction)
            return_prediction: Whether to include prediction details
            current_time: Current staining time (optional, for time-aware models)

        Returns:
            Dictionary containing:
                - cam: Raw CAM heatmap
                - overlay: Overlay image
                - predicted_class: Predicted class index
                - predicted_grade: Predicted grade (1-5)
                - confidence: Prediction confidence
                - probabilities: All class probabilities
        """
        # current_time is required for time-aware models
        if current_time is None:
            raise ValueError("current_time parameter is required for time-aware models")

        with torch.no_grad():
            output = self.model(input_tensor, current_time)

            # Handle multi-task model (returns tuple: grade_logits, time_deltas)
            if isinstance(output, tuple):
                output = output[0]  # Use only grade logits

            probs = F.softmax(output, dim=1)
            predicted_class = output.argmax(dim=1).item()
            confidence = probs[0, predicted_class].item()

        # Generate CAM for target class (or predicted class)
        cam = self.generate_cam(input_tensor, target_class, current_time)

        # Generate overlay
        overlay = self.generate_overlay(input_image, cam)

        result = {
            'cam': cam,
            'overlay': overlay,
        }

        if return_prediction:
            result.update({
                'predicted_class': predicted_class,
                'predicted_grade': predicted_class + 1,  # Convert 0-4 to 1-5
                'confidence': confidence,
                'probabilities': probs[0].cpu().numpy().tolist()
            })

        return result


class GradeExplainer:
    """High-level wrapper for explaining slide grade predictions with safe, conservative explanations"""

    # Visual observation descriptions (SAFE - no chemistry claims)
    VISUAL_OBSERVATIONS = {
        1: "Model detected very low staining intensity in cell regions",
        2: "Model detected low staining intensity with limited color contrast",
        3: "Model detected optimal staining intensity and color contrast",
        4: "Model detected high staining intensity with strong background signals",
        5: "Model detected very high staining intensity across wide areas"
    }

    # Grade labels for display
    GRADE_LABELS = {
        1: "Grade I (Under-stained)",
        2: "Grade II (Lightly stained)",
        3: "Grade III (Optimal)",
        4: "Grade IV (Over-stained)",
        5: "Grade V (Deeply over-stained)"
    }

    def __init__(self, model: nn.Module, device: str = 'cuda'):
        """Initialize explainer

        Args:
            model: Trained slide grading model
            device: Device to run on ('cuda' or 'cpu')
        """
        self.device = device
        self.model = model.to(device)
        self.model.eval()
        self.gradcam = GradCAM(self.model)

    def explain(
        self,
        input_tensor: torch.Tensor,
        input_image: np.ndarray,
        current_time: Optional[torch.Tensor] = None
    ) -> Dict:
        """Generate comprehensive explanation for slide grade

        Args:
            input_tensor: Preprocessed input tensor (1, C, H, W)
            input_image: Original image as numpy array (H, W, 3) in RGB
            current_time: Current staining time (optional, for time-aware models)

        Returns:
            Dictionary with:
                - grade_numeric: Predicted grade (1-5)
                - grade_label: Grade as Roman numeral
                - status: "PASS" or "FAIL"
                - confidence: Prediction confidence
                - reason: Likely failure reason (text)
                - cam_heatmap: Grad-CAM heatmap
                - overlay_image: Heatmap overlay on original
                - probabilities: All class probabilities
        """
        # Move tensor to device
        input_tensor = input_tensor.to(self.device)

        # current_time is required for time-aware models
        if current_time is None:
            raise ValueError("current_time parameter is required. User must provide staining time.")

        current_time = current_time.to(self.device)

        # Generate explanation
        explanation = self.gradcam.explain_prediction(
            input_tensor,
            input_image,
            return_prediction=True,
            current_time=current_time
        )

        # Extract prediction details
        grade_numeric = explanation['predicted_grade']
        grade_label = ['I', 'II', 'III', 'IV', 'V'][grade_numeric - 1]
        is_pass = (grade_numeric == 3)

        # Get visual observation (safe description)
        visual_observation = self.VISUAL_OBSERVATIONS.get(grade_numeric, "Unknown pattern")

        # Analyze heatmap pattern
        heatmap_analysis = self.analyze_heatmap_pattern(explanation['cam'], grade_numeric)

        # Generate comprehensive reason combining visual observation and heatmap analysis
        reason = f"{visual_observation}. {heatmap_analysis['interpretation']}"

        return {
            'grade_numeric': grade_numeric,
            'grade_label': grade_label,
            'status': 'PASS' if is_pass else 'FAIL',
            'confidence': explanation['confidence'],
            'reason': reason,
            'visual_observation': visual_observation,
            'heatmap_interpretation': heatmap_analysis['interpretation'],
            'cam_heatmap': explanation['cam'],
            'overlay_image': explanation['overlay'],
            'probabilities': explanation['probabilities']
        }

    def analyze_heatmap_pattern(self, cam: np.ndarray, grade: int) -> dict:
        """
        Analyze GradCAM heatmap patterns (SAFE - objective observations only)

        Args:
            cam: GradCAM heatmap (H, W) with values in [0, 1]
            grade: Predicted grade (1-5)

        Returns:
            Dictionary with interpretation
        """
        # Calculate activation statistics
        high_activation_threshold = 0.7

        high_activation_ratio = (cam > high_activation_threshold).mean()
        mean_activation = cam.mean()

        # Generate safe interpretation based on patterns
        if grade <= 2:  # Under-stained
            if high_activation_ratio < 0.15:
                interpretation = (
                    "Sparse activation pattern - model focused on limited regions "
                    "with weak intensity signals, consistent with under-staining."
                )
            else:
                interpretation = (
                    "Model detected limited color contrast in cell regions."
                )
        elif grade == 3:  # Optimal
            interpretation = (
                "Balanced activation pattern - model detected appropriate "
                "color contrast and cell visibility typical of optimal staining."
            )
        elif grade >= 4:  # Over-stained
            if high_activation_ratio > 0.4:
                interpretation = (
                    "Dense activation pattern - model focused on widespread intense signals "
                    "and background regions, consistent with over-staining."
                )
            else:
                interpretation = (
                    "Model detected high intensity signals in background regions."
                )
        else:
            interpretation = "Model analyzed staining intensity and distribution patterns."

        return {
            'high_activation_ratio': float(high_activation_ratio),
            'mean_activation': float(mean_activation),
            'interpretation': interpretation
        }

    def get_sop_checklist(self, grade: int, confidence: float) -> dict:
        """
        Get AMC SOP troubleshooting checklist (SAFE - general guidelines with disclaimers)

        Args:
            grade: Predicted grade (1-5)
            confidence: Model confidence (0-1)

        Returns:
            Dictionary with checklist items
        """
        checklist = {
            'disclaimer': (
                '⚠️ These are general troubleshooting suggestions based on AMC MM-SOP-03C. '
                'Consult laboratory supervisor for diagnosis and corrective actions.'
            ),
            'grade_label': self.GRADE_LABELS.get(grade, "Unknown"),
            'visual_indication': self.VISUAL_OBSERVATIONS.get(grade, "Unknown pattern"),
            'checklist_items': []
        }

        if grade <= 2:  # Under-stained
            checklist['category'] = 'Under-staining indicators'
            checklist['checklist_items'] = [
                'General troubleshooting checklist for under-staining (AMC MM-SOP-03C):',
                '  □ Verify staining time was sufficient for the dilution method',
                '  □ Check Giemsa working solution concentration (3% or 10%)',
                '  □ Confirm buffered water pH = 7.2 ± 0.1',
                '  □ Verify stock Giemsa quality (perform QC check)',
                '  □ Ensure methanol fixation was adequate (thin smears)',
                '  □ Check that stain solution is freshly prepared',
                '  □ Consult supervisor if issue persists'
            ]
        elif grade == 3:  # Optimal
            checklist['category'] = 'Optimal staining'
            checklist['checklist_items'] = [
                '✓ Slide meets AMC quality standards',
                '✓ Proceed with malaria parasite examination',
                '✓ Document staining time and conditions for batch records'
            ]
        elif grade >= 4:  # Over-stained
            checklist['category'] = 'Over-staining indicators'
            checklist['checklist_items'] = [
                'General troubleshooting checklist for over-staining (AMC MM-SOP-03C):',
                '  □ Verify staining time (may be too long for dilution method)',
                '  □ Inspect stain solution for visible precipitates',
                '  □ Confirm buffered water pH = 7.2 ± 0.1',
                '  □ Check if working solution concentration is too high',
                '  □ Verify stock Giemsa quality and expiration date',
                '  □ Filter stain solution to remove precipitates if present',
                '  □ Review methanol fixation protocol',
                '  □ Consult supervisor if issue persists'
            ]

        if confidence < 0.7:
            checklist['checklist_items'].append(
                '  □ Low confidence - verify image quality, focus, and microscope settings'
            )

        return checklist

    def save_visualization(
        self,
        overlay_image: np.ndarray,
        save_path: str
    ):
        """Save visualization to file

        Args:
            overlay_image: Overlay image from explain()
            save_path: Path to save image
        """
        overlay_pil = Image.fromarray(overlay_image)
        overlay_pil.save(save_path)
