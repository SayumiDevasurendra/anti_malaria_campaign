"""
Stain Time Optimization - Main Streamlit Application

Multi-page application for Giemsa staining time optimization and slide quality grading.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src'))

# Page configuration
st.set_page_config(
    page_title="Stain Time Optimization",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<div class="main-header">🔬 Stain Time Optimization System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Giemsa Staining Time Determination via Slide Grading</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1f77b4/ffffff?text=AMC+Logo", use_container_width=True)
    st.markdown("---")

    st.markdown("### 📋 Navigation")
    st.info("""
    Use the pages in the sidebar to access different features:

    - **🏠 Home**: Overview and quick start
    - **🎯 Single Slide Grading**: Grade individual slides
    - **⏱️ Optimal Time Finder**: Minute-by-minute sweep analysis
    - **📊 Batch Analysis**: Analyze multiple batches
    - **📈 Pattern Viewer**: National staining time patterns
    """)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Component:** Stain Time Optimization
    **Author:** Sayumi Devasurendra
    **Version:** 0.1.0

    This system determines optimal Giemsa staining times for 10% and 3% working solutions.
    """)

# Main content
st.markdown("## 🎯 System Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>🎯 Slide Grading</h3>
        <p>Automated grading of Giemsa-stained slides using AMC criteria (Grades I-V)</p>
        <ul>
            <li>Single slide analysis</li>
            <li>Confidence scores</li>
            <li>Pass/fail determination</li>
            <li>Failure diagnosis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>⏱️ Optimal Time Selection</h3>
        <p>Find the earliest acceptable staining time for each batch</p>
        <ul>
            <li>Minute-by-minute sweep</li>
            <li>10% rapid method (5-15 min)</li>
            <li>3% slow method (30-45 min)</li>
            <li>Stability analysis</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>📊 Batch Analytics</h3>
        <p>Track and analyze staining patterns across batches and sites</p>
        <ul>
            <li>Batch comparison</li>
            <li>Site-level patterns</li>
            <li>National aggregation</li>
            <li>Trend visualization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Quick Start Guide
st.markdown("## 🚀 Quick Start Guide")

with st.expander("📖 How to Use This System", expanded=False):
    st.markdown("""
    ### Step 1: Single Slide Grading
    1. Go to **🎯 Single Slide Grading** page
    2. Upload a slide image (thin or thick smear)
    3. View grade (I-V), confidence, and pass/fail status
    4. Get failure diagnosis if needed

    ### Step 2: Find Optimal Staining Time
    1. Go to **⏱️ Optimal Time Finder** page
    2. Select dilution (10% or 3%)
    3. Upload images for minute-by-minute sweep
    4. System recommends earliest acceptable minute

    ### Step 3: Batch Analysis
    1. Go to **📊 Batch Analysis** page
    2. Upload batch metadata CSV
    3. Compare optimal times across batches
    4. Track site-level patterns

    ### Step 4: View National Patterns
    1. Go to **📈 Pattern Viewer** page
    2. Explore aggregated staining time data
    3. See recommended starting times by region
    """)

# AMC Grade Scale Reference
st.markdown("## 📚 AMC Grade Scale Reference")

grade_data = {
    "Grade": ["I", "II", "III", "IV", "V"],
    "Quality": ["Excellent", "Good", "Acceptable", "Poor", "Unacceptable"],
    "Status": ["✅ Pass", "✅ Pass", "✅ Pass (Minimum)", "❌ Fail", "❌ Fail"],
    "Description": [
        "Optimal staining, clear contrast",
        "Good staining, acceptable contrast",
        "Minimum passing grade",
        "Suboptimal staining",
        "Unusable slide"
    ]
}

st.table(grade_data)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>Anti-Malaria Campaign Sri Lanka | Stain Time Optimization Component</p>
    <p>For support, contact: Sayumi Devasurendra</p>
</div>
""", unsafe_allow_html=True)
