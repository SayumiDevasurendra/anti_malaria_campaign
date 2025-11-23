"""
Staining Time Optimizer Module

Determines optimal Giemsa staining time from minute-by-minute sweeps and provides
SOP-aligned failure diagnosis with corrective actions.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from collections import defaultdict


class StainingTimeOptimizer:
    """Select optimal staining time from minute-by-minute sweep"""

    def __init__(
        self,
        model: nn.Module,
        device: str = 'cuda',
        pass_threshold: int = 3,  # AMC: ONLY Grade III is acceptable (not >= III)
        confidence_threshold: float = 0.8,
        stability_window: int = 2  # Consecutive acceptable minutes
    ):
        """
        Initialize optimal time selector

        Args:
            model: Trained grade classification model
            device: Device ('cuda' or 'cpu')
            pass_threshold: ONLY this exact grade is acceptable (AMC: Grade III only)
            confidence_threshold: Minimum confidence for pass prediction
            stability_window: Number of consecutive acceptable minutes
        """
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.pass_threshold = pass_threshold  # AMC: ONLY Grade III = 3 (not >= 3)
        self.confidence_threshold = confidence_threshold
        self.stability_window = stability_window

    @torch.no_grad()
    def predict_grade(self, images: torch.Tensor) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Predict grades and confidences for images

        Args:
            images: Batch of images (B, C, H, W)

        Returns:
            Tuple of (predicted_grades, confidences, probabilities)
        """
        images = images.to(self.device)

        # Forward pass
        logits = self.model(images)
        probs = F.softmax(logits, dim=1)

        # Get predictions and confidences
        confidences, predictions = torch.max(probs, dim=1)

        # Convert to 1-5 scale (from 0-4)
        grades = predictions.cpu().numpy() + 1
        confidences = confidences.cpu().numpy()
        probs = probs.cpu().numpy()

        return grades, confidences, probs

    def compute_pass_probability(self, probs: np.ndarray) -> float:
        """
        Compute probability of passing (ONLY Grade == pass_threshold, per AMC)

        Args:
            probs: Probability distribution over grades (num_samples, num_classes)

        Returns:
            Probability of achieving the exact passing grade (AMC: Grade III only)
        """
        # AMC: ONLY Grade III is acceptable (not >= III)
        # Grades are 0-indexed, so pass_threshold=3 means index=2
        pass_idx = self.pass_threshold - 1
        pass_prob = probs[:, pass_idx].mean()  # Only this specific grade, not >= threshold

        return pass_prob

    def analyze_minute(
        self,
        images: torch.Tensor,
        minute: int
    ) -> Dict:
        """
        Analyze slides from a specific minute

        Args:
            images: Images from this minute
            minute: Staining time in minutes

        Returns:
            Analysis dictionary
        """
        grades, confidences, probs = self.predict_grade(images)

        # Compute pass probability
        pass_prob = self.compute_pass_probability(probs)

        # Pass/fail decision
        is_pass = pass_prob >= self.confidence_threshold

        analysis = {
            'minute': minute,
            'num_images': len(images),
            'predicted_grades': grades,
            'mean_grade': grades.mean(),
            'std_grade': grades.std(),
            'confidences': confidences,
            'mean_confidence': confidences.mean(),
            'pass_probability': pass_prob,
            'is_pass': is_pass,
            'grade_distribution': {
                i + 1: (grades == i + 1).sum() for i in range(5)
            }
        }

        return analysis

    def select_optimal_minute(
        self,
        minute_analyses: Dict[int, Dict]
    ) -> Dict:
        """
        Select earliest acceptable minute from sweep analyses

        Args:
            minute_analyses: Dictionary mapping minute -> analysis results

        Returns:
            Selection result with optimal minute and reasoning
        """
        # Sort minutes
        sorted_minutes = sorted(minute_analyses.keys())

        # Find passing minutes
        passing_minutes = [
            m for m in sorted_minutes
            if minute_analyses[m]['is_pass']
        ]

        if not passing_minutes:
            return {
                'optimal_minute': None,
                'status': 'no_pass',
                'message': 'No minute achieved passing grade. Check stain quality and preparation.',
                'all_analyses': minute_analyses
            }

        # Find earliest stable minute (consecutive passing)
        optimal_minute = None

        for i in range(len(passing_minutes) - self.stability_window + 1):
            window = passing_minutes[i:i + self.stability_window]

            # Check if consecutive
            if all(window[j] == window[j - 1] + 1 for j in range(1, len(window))):
                optimal_minute = window[0]
                break

        # If no stable window found, take earliest passing minute
        if optimal_minute is None:
            optimal_minute = passing_minutes[0]
            stability_note = "Warning: No stable window found. Consider verifying stain quality."
        else:
            stability_note = f"Stable for {self.stability_window} consecutive minutes"

        result = {
            'optimal_minute': optimal_minute,
            'status': 'success',
            'message': f"Recommended staining time: {optimal_minute} minutes",
            'stability_note': stability_note,
            'pass_probability': minute_analyses[optimal_minute]['pass_probability'],
            'mean_grade': minute_analyses[optimal_minute]['mean_grade'],
            'mean_confidence': minute_analyses[optimal_minute]['mean_confidence'],
            'passing_minutes': passing_minutes,
            'all_analyses': minute_analyses
        }

        return result

    def explain_failure(self, analysis: Dict) -> Dict:
        """
        Provide AMC MM-SOP-03C compliant explanation for failing slides

        Args:
            analysis: Analysis results for a failing slide

        Returns:
            Explanation with reason codes and quick fixes per AMC guidelines
        """
        mean_grade = analysis['mean_grade']
        pass_prob = analysis['pass_probability']

        reasons = []
        fixes = []

        # AMC: Only Grade III is acceptable
        # Grades I-II: Under-staining
        if mean_grade < self.pass_threshold:
            grade_round = round(mean_grade)
            if grade_round <= 1:
                reasons.append("grade_i_under_stain")
                fixes.extend([
                    "Increase staining time by 2-3 minutes",
                    "Check Giemsa working solution concentration (should be 3% or 10%)",
                    "Verify stock Giemsa quality (perform QC check)",
                    "Check buffered water pH (should be 7.2)"
                ])
            else:  # Grade II
                reasons.append("grade_ii_light_stain")
                fixes.extend([
                    "Increase staining time by 1-2 minutes",
                    "Verify Giemsa concentration is accurate",
                    "Check that methanol fixation was adequate (thin smear)",
                    "Ensure stain solution is freshly prepared"
                ])

        # Grades IV-V: Over-staining
        elif mean_grade > self.pass_threshold:
            grade_round = round(mean_grade)
            if grade_round >= 5:
                reasons.append("grade_v_deep_over_stain")
                fixes.extend([
                    "Decrease staining time by 2-4 minutes",
                    "Replace Giemsa working solution (may be contaminated or too old)",
                    "Verify buffered water pH (high pH causes bluish/purple over-staining)",
                    "Check stock Giemsa quality (perform QC check per MM-SOP-03C)",
                    "Ensure proper methanol fixation (over-fixation can cause deep staining)",
                    "Filter stain to remove precipitates"
                ])
            else:  # Grade IV
                reasons.append("grade_iv_over_stain")
                fixes.extend([
                    "Decrease staining time by 1-2 minutes",
                    "Check for Giemsa precipitates (filter or replace stain)",
                    "Verify buffered water pH is exactly 7.2 (low pH causes pinkish/over-staining)",
                    "Check if working solution is too concentrated"
                ])

        # Low confidence (could be multiple issues)
        if analysis['mean_confidence'] < 0.6:
            reasons.append("low_confidence")
            fixes.extend([
                "Check image quality and focus",
                "Verify buffered water pH (should be 7.2)",
                "Filter or replace Giemsa stain if precipitates visible"
            ])

        # High variance in grades
        if analysis['std_grade'] > 1.0:
            reasons.append("high_variance")
            fixes.append("Check slide fixation and staining uniformity")

        explanation = {
            'minute': analysis['minute'],
            'status': 'fail',
            'predicted_grade': round(mean_grade, 1),
            'pass_probability': pass_prob,
            'reason_codes': reasons,
            'sop_explanation': self._format_sop_explanation(reasons),
            'quick_fixes': fixes
        }

        return explanation

    def _format_sop_explanation(self, reason_codes: List[str]) -> str:
        """Format reason codes into AMC MM-SOP-03C compliant language"""
        explanations = {
            'grade_i_under_stain': "Grade I - Under-stained (incomplete lysis, parasites not visible)",
            'grade_ii_light_stain': "Grade II - Lightly stained (suboptimal color contrast)",
            'grade_iv_over_stain': "Grade IV - Over-stained (reduced color contrast, background blue-grey)",
            'grade_v_deep_over_stain': "Grade V - Deeply over-stained (poor contrast, dark blue-grey background)",
            'low_confidence': "Low model confidence (possible image quality or preparation issues)",
            'high_variance': "High grade variance (inconsistent staining across slide)",
            'precipitates': "Possible dye precipitates detected",
            'ph_rinse_issue': "Possible pH or rinse issue (check buffered water at pH 7.2)"
        }

        return "; ".join([explanations.get(code, code) for code in reason_codes])


class BatchOptimalTimeTracker:
    """Track optimal minutes across batches and sites"""

    def __init__(self, storage_path: str = 'data/optimal_times.csv'):
        """
        Initialize tracker

        Args:
            storage_path: Path to store historical records
        """
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing records
        if self.storage_path.exists():
            self.records = pd.read_csv(self.storage_path)
        else:
            self.records = pd.DataFrame(columns=[
                'batch_id', 'site', 'dilution', 'optimal_minute',
                'pass_probability', 'mean_grade', 'timestamp'
            ])

    def add_record(
        self,
        batch_id: str,
        site: str,
        dilution: str,
        optimal_minute: int,
        pass_probability: float,
        mean_grade: float
    ):
        """Add new optimal time record"""
        import datetime

        new_record = {
            'batch_id': batch_id,
            'site': site,
            'dilution': dilution,
            'optimal_minute': optimal_minute,
            'pass_probability': pass_probability,
            'mean_grade': mean_grade,
            'timestamp': datetime.datetime.now().isoformat()
        }

        self.records = pd.concat([
            self.records,
            pd.DataFrame([new_record])
        ], ignore_index=True)

        # Save
        self.records.to_csv(self.storage_path, index=False)

    def get_site_pattern(self, dilution: str) -> Dict:
        """Get optimal time pattern for a dilution"""
        subset = self.records[self.records['dilution'] == dilution]

        if len(subset) == 0:
            return {'dilution': dilution, 'data': 'insufficient'}

        pattern = {
            'dilution': dilution,
            'mean_optimal_minute': subset['optimal_minute'].mean(),
            'std_optimal_minute': subset['optimal_minute'].std(),
            'median_optimal_minute': subset['optimal_minute'].median(),
            'mode_optimal_minute': subset['optimal_minute'].mode().values[0] if len(subset) > 0 else None,
            'num_batches': len(subset),
            'sites': subset['site'].unique().tolist()
        }

        return pattern
