"""
Single Slide Grading Page

Upload and analyze individual Giemsa-stained slide images for quality grading.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import streamlit as st
import sys
from pathlib import Path
import torch
from PIL import Image
import numpy as np
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_classifier import create_slide_grade_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.staining_time_optimizer import StainingTimeOptimizer

st.set_page_config(page_title="Single Slide Grading", page_icon="🎯", layout="wide")

# Page title
st.title("🎯 Single Slide Grading")
st.markdown("Upload a Giemsa-stained slide image to get automated quality grading (AMC Grades I-V)")

# Sidebar - Model Selection
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    model_path = st.text_input(
        "Model Checkpoint Path",
        value="checkpoints/best_model.pth",
        help="Path to trained model checkpoint"
    )

    confidence_threshold = st.slider(
        "Pass Confidence Threshold",
        min_value=0.5,
        max_value=1.0,
        value=0.8,
        step=0.05,
        help="Minimum confidence for pass/fail decision"
    )

    st.markdown("---")

    st.markdown("### 📊 Grade Scale")
    st.markdown("""
    - **Grade I**: Excellent ✅
    - **Grade II**: Good ✅
    - **Grade III**: Acceptable ✅
    - **Grade IV**: Poor ❌
    - **Grade V**: Unacceptable ❌

    **Pass Threshold**: Grade III or better
    """)

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("### 📤 Upload Slide Image")

    uploaded_file = st.file_uploader(
        "Choose a slide image",
        type=['jpg', 'jpeg', 'png', 'tif', 'tiff'],
        help="Upload a Giemsa-stained thin or thick smear image"
    )

    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Slide", use_container_width=True)

        # Metadata inputs
        st.markdown("### 📝 Slide Metadata (Optional)")

        meta_col1, meta_col2 = st.columns(2)

        with meta_col1:
            dilution = st.selectbox("Dilution", ["10%", "3%", "Unknown"])
            smear_type = st.selectbox("Smear Type", ["thin", "thick", "unknown"])

        with meta_col2:
            stain_time = st.number_input("Staining Time (min)", min_value=0, value=0, step=1)
            batch_id = st.text_input("Batch ID", value="", placeholder="Optional")

with col2:
    st.markdown("### 🔬 Analysis Results")

    if uploaded_file and st.button("🚀 Analyze Slide", type="primary"):
        with st.spinner("Analyzing slide..."):
            try:
                # Load image
                image = Image.open(uploaded_file).convert('RGB')

                # Load model
                @st.cache_resource
                def load_model(model_path):
                    if not Path(model_path).exists():
                        st.error(f"Model not found: {model_path}")
                        return None

                    model = create_slide_grade_model(architecture='resnet18', num_grade_classes=5)
                    checkpoint = torch.load(model_path, map_location='cpu')
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.eval()
                    return model

                model = load_model(model_path)

                if model is not None:
                    # Transform image
                    transform = get_stain_time_val_transforms((512, 512))
                    image_tensor = transform(image).unsqueeze(0)

                    # Predict
                    with torch.no_grad():
                        logits = model(image_tensor)
                        probs = torch.softmax(logits, dim=1)
                        confidence, prediction = torch.max(probs, dim=1)

                        grade_numeric = prediction.item() + 1  # Convert 0-4 to 1-5
                        grade_label = ['I', 'II', 'III', 'IV', 'V'][prediction.item()]
                        confidence_score = confidence.item()

                    # Determine pass/fail
                    is_pass = grade_numeric >= 3

                    # Display results
                    st.markdown("#### 📊 Grading Results")

                    # Metrics
                    metric_col1, metric_col2, metric_col3 = st.columns(3)

                    with metric_col1:
                        st.metric("Grade", f"Grade {grade_label}", delta=None)

                    with metric_col2:
                        st.metric("Confidence", f"{confidence_score:.1%}", delta=None)

                    with metric_col3:
                        status_emoji = "✅" if is_pass else "❌"
                        status_text = "PASS" if is_pass else "FAIL"
                        st.metric("Status", f"{status_emoji} {status_text}", delta=None)

                    # Detailed results
                    st.markdown("---")

                    if is_pass:
                        st.success(f"✅ **Slide Passed**: Grade {grade_label} with {confidence_score:.1%} confidence")
                        st.info("This slide is acceptable for parasite examination.")
                    else:
                        st.error(f"❌ **Slide Failed**: Grade {grade_label} with {confidence_score:.1%} confidence")

                        # Failure diagnosis
                        st.markdown("#### 🔍 Failure Diagnosis")

                        if grade_numeric < 3:
                            st.warning("**Likely Issue**: Under-staining (too pale)")
                            st.markdown("""
                            **Corrective Actions**:
                            - Increase staining time by 1-2 minutes
                            - Check Giemsa concentration
                            - Verify stain is fresh
                            """)
                        else:
                            st.warning("**Likely Issue**: Over-staining or poor quality")
                            st.markdown("""
                            **Corrective Actions**:
                            - Decrease staining time by 1-2 minutes
                            - Check for precipitates (filter/replace stain)
                            - Verify buffered water pH (7.2)
                            - Check fixation quality
                            """)

                    # Probability distribution
                    st.markdown("#### 📈 Grade Probability Distribution")

                    prob_data = {
                        "Grade": ["I", "II", "III", "IV", "V"],
                        "Probability": [f"{p:.1%}" for p in probs[0].tolist()]
                    }
                    st.bar_chart(probs[0].numpy(), use_container_width=True)
                    st.dataframe(prob_data, use_container_width=True)

                    # Export results
                    st.markdown("---")
                    st.markdown("#### 💾 Export Results")

                    results_dict = {
                        "filename": uploaded_file.name,
                        "grade_numeric": grade_numeric,
                        "grade_label": grade_label,
                        "confidence": confidence_score,
                        "status": "PASS" if is_pass else "FAIL",
                        "dilution": dilution,
                        "smear_type": smear_type,
                        "stain_time_min": stain_time if stain_time > 0 else None,
                        "batch_id": batch_id if batch_id else None
                    }

                    results_df = pd.DataFrame([results_dict])
                    csv = results_df.to_csv(index=False)

                    st.download_button(
                        label="📥 Download Results (CSV)",
                        data=csv,
                        file_name=f"grading_result_{uploaded_file.name}.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Error analyzing slide: {str(e)}")
                st.exception(e)

    else:
        st.info("👆 Upload a slide image and click 'Analyze Slide' to get started")

# Tips section
st.markdown("---")

with st.expander("💡 Tips for Best Results"):
    st.markdown("""
    ### Image Quality Requirements
    - **Format**: JPG, PNG, TIF, or TIFF
    - **Resolution**: At least 1024×768 pixels recommended
    - **Focus**: Image should be in focus
    - **Lighting**: Consistent, even illumination
    - **Field of View**: Capture representative area of slide

    ### Interpretation Guidelines
    - **Confidence < 70%**: Results may be unreliable, consider re-imaging
    - **Grade III**: Minimum acceptable quality for diagnosis
    - **Failed Slides**: Follow corrective actions before re-staining

    ### Common Issues
    - **Low Confidence**: Check image quality (focus, lighting)
    - **Consistent Failures**: Check staining protocol and reagents
    - **Variable Grades**: Ensure consistent imaging conditions
    """)
