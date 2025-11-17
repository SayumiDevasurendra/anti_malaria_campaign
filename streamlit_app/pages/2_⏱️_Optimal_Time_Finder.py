"""
Optimal Staining Time Finder Page

Analyze minute-by-minute sweep to find optimal Giemsa staining time.

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
import plotly.express as px
import plotly.graph_objects as go

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / 'src'))

from models.slide_grade_classifier import create_slide_grade_model
from data.stain_time_transforms import get_stain_time_val_transforms
from evaluation.staining_time_optimizer import StainingTimeOptimizer

st.set_page_config(page_title="Optimal Time Finder", page_icon="⏱️", layout="wide")

# Page title
st.title("⏱️ Optimal Staining Time Finder")
st.markdown("Upload minute-by-minute sweep images to find the earliest acceptable staining time")

# Sidebar settings
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    model_path = st.text_input(
        "Model Checkpoint",
        value="checkpoints/best_model.pth"
    )

    dilution = st.selectbox(
        "Dilution Method",
        options=["10%", "3%"],
        help="10% rapid (5-15 min) or 3% slow (30-45 min)"
    )

    # Time range based on dilution
    if dilution == "10%":
        default_range = (5, 15)
        st.info("**10% Rapid Method**\n\nTypical range: 5-15 minutes\nOptimal: ~8-10 minutes")
    else:
        default_range = (30, 45)
        st.info("**3% Slow Method**\n\nTypical range: 30-45 minutes\nOptimal: ~30-35 minutes")

    min_time = st.number_input("Minimum Time (min)", value=default_range[0], min_value=1)
    max_time = st.number_input("Maximum Time (min)", value=default_range[1], min_value=min_time)

    st.markdown("---")

    st.markdown("### 📊 AMC Acceptance Criteria")
    st.info("""
    **Grade III ONLY** (per AMC MM-SOP-03C)

    Only Grade III provides optimal color
    contrast for accurate parasite identification.
    """)

    pass_threshold = 3  # AMC: Only Grade III is acceptable
    confidence_threshold = st.slider("Pass Confidence", 0.5, 1.0, 0.8, 0.05, help="Minimum confidence for accepting Grade III")
    stability_window = st.number_input("Stability Window (min)", 1, 5, 2, help="Consecutive passing minutes required")

# Main content
st.markdown("### 📤 Upload Sweep Images")

st.info(f"""
**Instructions**:
1. Upload images for each minute in the range ({min_time}-{max_time} minutes)
2. Name files as: `{dilution}_Xmin_[grade]_[smear].jpg` (e.g., `{dilution}_8min_III_thin.jpg`)
3. Or manually assign times below
""")

uploaded_files = st.file_uploader(
    "Upload slide images",
    type=['jpg', 'jpeg', 'png', 'tif', 'tiff'],
    accept_multiple_files=True,
    help="Upload one or more images from minute-by-minute sweep"
)

if uploaded_files:
    st.success(f"✅ Uploaded {len(uploaded_files)} images")

    # Manual time assignment
    st.markdown("### ⏱️ Assign Staining Times")

    time_assignments = {}

    # Create grid for file-time assignment
    num_cols = 3
    cols = st.columns(num_cols)

    for idx, file in enumerate(uploaded_files):
        with cols[idx % num_cols]:
            # Try to extract time from filename
            import re
            match = re.search(r'(\d+)min', file.name)
            default_time = int(match.group(1)) if match else min_time + idx

            assigned_time = st.number_input(
                f"Time for {file.name[:20]}...",
                value=default_time,
                min_value=min_time,
                max_value=max_time,
                key=f"time_{idx}"
            )
            time_assignments[file.name] = assigned_time

    # Analyze button
    st.markdown("---")

    if st.button("🔍 Analyze Sweep & Find Optimal Time", type="primary"):
        with st.spinner("Analyzing minute-by-minute sweep..."):
            try:
                # Load model
                @st.cache_resource
                def load_model(model_path):
                    model = create_slide_grade_model(architecture='resnet18', num_grade_classes=5)
                    checkpoint = torch.load(model_path, map_location='cpu')
                    model.load_state_dict(checkpoint['model_state_dict'])
                    model.eval()
                    return model

                model = load_model(model_path)

                # Initialize optimizer
                optimizer = StainingTimeOptimizer(
                    model=model,
                    device='cpu',
                    pass_threshold=pass_threshold,
                    confidence_threshold=confidence_threshold,
                    stability_window=stability_window
                )

                # Analyze each minute
                minute_analyses = {}
                transform = get_stain_time_val_transforms((512, 512))

                progress_bar = st.progress(0)

                for idx, file in enumerate(uploaded_files):
                    minute = time_assignments[file.name]

                    # Load and process image
                    image = Image.open(file).convert('RGB')
                    image_tensor = transform(image).unsqueeze(0)

                    # Get predictions
                    with torch.no_grad():
                        logits = model(image_tensor)
                        probs = torch.softmax(logits, dim=1)

                    # Analyze minute
                    grades = (torch.argmax(probs, dim=1) + 1).numpy()
                    confidences = torch.max(probs, dim=1)[0].numpy()

                    # Compute pass probability (AMC: Only Grade III is acceptable)
                    # pass_threshold = 3, so index is 2 (0-indexed)
                    pass_prob = probs[:, (pass_threshold-1)].mean().item()

                    minute_analyses[minute] = {
                        'minute': minute,
                        'num_images': 1,
                        'predicted_grades': grades,
                        'mean_grade': grades.mean(),
                        'std_grade': 0.0,
                        'confidences': confidences,
                        'mean_confidence': confidences.mean(),
                        'pass_probability': pass_prob,
                        'is_pass': pass_prob >= confidence_threshold,
                        'grade_distribution': {i+1: int(grades == i+1).sum() for i in range(5)}
                    }

                    progress_bar.progress((idx + 1) / len(uploaded_files))

                # Select optimal minute
                result = optimizer.select_optimal_minute(minute_analyses)

                # Display results
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")

                if result['status'] == 'success':
                    # Success - found optimal minute
                    st.success(f"✅ **Optimal Staining Time Found: {result['optimal_minute']} minutes**")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Optimal Time", f"{result['optimal_minute']} min", delta=None)

                    with col2:
                        st.metric("Pass Probability", f"{result['pass_probability']:.1%}", delta=None)

                    with col3:
                        st.metric("Mean Grade", f"{result['mean_grade']:.1f}", delta=None)

                    st.info(result['stability_note'])

                    # Show all passing minutes
                    if len(result['passing_minutes']) > 1:
                        st.markdown(f"**All Passing Minutes**: {', '.join(map(str, result['passing_minutes']))} min")

                else:
                    # Failed to find optimal minute
                    st.error(f"❌ **{result['message']}**")
                    st.warning("No minute in the sweep achieved passing grade. Review staining protocol.")

                # Visualization - Pass Probability over Time
                st.markdown("### 📈 Pass Probability Across Minutes")

                minutes_list = sorted(minute_analyses.keys())
                pass_probs = [minute_analyses[m]['pass_probability'] for m in minutes_list]
                mean_grades = [minute_analyses[m]['mean_grade'] for m in minutes_list]

                fig = go.Figure()

                # Pass probability line
                fig.add_trace(go.Scatter(
                    x=minutes_list,
                    y=pass_probs,
                    name='Pass Probability',
                    line=dict(color='blue', width=3),
                    mode='lines+markers'
                ))

                # Threshold line
                fig.add_hline(
                    y=confidence_threshold,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Pass Threshold ({confidence_threshold:.0%})"
                )

                # Mark optimal minute
                if result['status'] == 'success':
                    fig.add_vline(
                        x=result['optimal_minute'],
                        line_dash="dot",
                        line_color="green",
                        annotation_text=f"Optimal: {result['optimal_minute']} min"
                    )

                fig.update_layout(
                    title="Pass Probability vs Staining Time",
                    xaxis_title="Staining Time (minutes)",
                    yaxis_title="Pass Probability",
                    yaxis_range=[0, 1],
                    hovermode='x unified'
                )

                st.plotly_chart(fig, use_container_width=True)

                # Detailed table
                st.markdown("### 📋 Detailed Minute-by-Minute Results")

                table_data = []
                for minute in sorted(minute_analyses.keys()):
                    analysis = minute_analyses[minute]
                    table_data.append({
                        "Time (min)": minute,
                        "Mean Grade": f"{analysis['mean_grade']:.1f}",
                        "Pass Probability": f"{analysis['pass_probability']:.1%}",
                        "Confidence": f"{analysis['mean_confidence']:.1%}",
                        "Status": "✅ Pass" if analysis['is_pass'] else "❌ Fail"
                    })

                st.dataframe(table_data, use_container_width=True)

                # Export results
                st.markdown("---")
                st.markdown("### 💾 Export Results")

                export_data = {
                    "dilution": dilution,
                    "optimal_minute": result.get('optimal_minute', None),
                    "pass_probability": result.get('pass_probability', None),
                    "status": result['status'],
                    "message": result['message'],
                    "passing_minutes": ','.join(map(str, result.get('passing_minutes', []))),
                    "total_minutes_tested": len(minute_analyses)
                }

                export_df = pd.DataFrame([export_data])
                csv = export_df.to_csv(index=False)

                st.download_button(
                    "📥 Download Summary (CSV)",
                    data=csv,
                    file_name=f"optimal_time_{dilution}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")
                st.exception(e)

else:
    st.info("👆 Upload sweep images to begin analysis")

# Tips
st.markdown("---")

with st.expander("💡 Tips for Optimal Time Finding"):
    st.markdown("""
    ### Best Practices

    **Image Collection**:
    - Take images at regular 1-minute intervals
    - Use consistent magnification and lighting
    - Capture representative field of view
    - Include both thin and thick smears if possible

    **Sweep Range**:
    - **10% method**: Test 5-15 minutes (typical optimal: 8-10 min)
    - **3% method**: Test 30-45 minutes (typical optimal: 30-35 min)

    **Interpretation**:
    - **Optimal minute**: Earliest time that achieves Grade III (AMC requirement)
    - **Stability window**: Ensures consistency (2+ consecutive passing minutes)
    - **Pass probability**: Model's confidence that slide is Grade III (not II or IV)

    ### Troubleshooting

    - **No passing minutes**: Check stain quality, pH (7.2), fixation
    - **Variable results**: Ensure consistent imaging and sample preparation
    - **Low confidence**: Review image quality or increase sample size
    """)
