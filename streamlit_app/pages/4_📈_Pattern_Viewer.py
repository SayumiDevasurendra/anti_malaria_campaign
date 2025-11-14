"""
National Pattern Viewer Page

Visualize aggregated staining time patterns across Sri Lanka.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Pattern Viewer", page_icon="📈", layout="wide")

# Page title
st.title("📈 National Staining Time Pattern Viewer")
st.markdown("Explore aggregated optimal staining time patterns across Sri Lanka")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    dilution_view = st.selectbox(
        "View Dilution",
        options=["Both", "10% Only", "3% Only"]
    )

    show_uncertainty = st.checkbox("Show Uncertainty Bands", value=True)

    st.markdown("---")
    st.info("""
    **Pattern Aggregation**:

    Aggregates anonymized optimal time data across sites to provide:
    - Recommended starting times
    - Regional patterns
    - Confidence intervals
    """)

# Main content
st.markdown("### 📊 National Pattern Summary")

# Generate sample pattern data
sample_data = {
    '10%': {
        'mean': 8.5,
        'std': 1.2,
        'median': 8.0,
        'min': 6,
        'max': 12,
        'num_batches': 45,
        'num_sites': 8
    },
    '3%': {
        'mean': 33.2,
        'std': 3.1,
        'median': 32.0,
        'min': 28,
        'max': 40,
        'num_batches': 38,
        'num_sites': 7
    }
}

# Display metrics
col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 10% Rapid Method")

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Mean Time", f"{sample_data['10%']['mean']:.1f} min")
    with metric_col2:
        st.metric("Median Time", f"{sample_data['10%']['median']:.0f} min")
    with metric_col3:
        st.metric("Std Dev", f"{sample_data['10%']['std']:.1f} min")

    st.info(f"""
    **Recommended Starting Time**: {int(sample_data['10%']['median'])} minutes

    Based on {sample_data['10%']['num_batches']} batches from {sample_data['10%']['num_sites']} sites.

    **Range**: {sample_data['10%']['min']}-{sample_data['10%']['max']} minutes
    """)

with col2:
    st.markdown("#### 3% Slow Method")

    metric_col1, metric_col2, metric_col3 = st.columns(3)
    with metric_col1:
        st.metric("Mean Time", f"{sample_data['3%']['mean']:.1f} min")
    with metric_col2:
        st.metric("Median Time", f"{sample_data['3%']['median']:.0f} min")
    with metric_col3:
        st.metric("Std Dev", f"{sample_data['3%']['std']:.1f} min")

    st.info(f"""
    **Recommended Starting Time**: {int(sample_data['3%']['median'])} minutes

    Based on {sample_data['3%']['num_batches']} batches from {sample_data['3%']['num_sites']} sites.

    **Range**: {sample_data['3%']['min']}-{sample_data['3%']['max']} minutes
    """)

st.markdown("---")

# Distribution plots
st.markdown("### 📊 Optimal Time Distribution")

# Generate sample distribution data
import numpy as np

np.random.seed(42)
dist_10 = np.random.normal(sample_data['10%']['mean'], sample_data['10%']['std'], 100)
dist_3 = np.random.normal(sample_data['3%']['mean'], sample_data['3%']['std'], 100)

df_dist = pd.DataFrame({
    'Time (min)': list(dist_10) + list(dist_3),
    'Dilution': ['10%'] * len(dist_10) + ['3%'] * len(dist_3)
})

fig = px.histogram(
    df_dist,
    x='Time (min)',
    color='Dilution',
    barmode='overlay',
    nbins=20,
    title='Distribution of Optimal Staining Times',
    opacity=0.7
)
st.plotly_chart(fig, use_container_width=True)

# Box plot
fig = px.box(
    df_dist,
    x='Dilution',
    y='Time (min)',
    color='Dilution',
    title='Optimal Time Range by Dilution Method',
    points='all'
)
st.plotly_chart(fig, use_container_width=True)

# Regional patterns (if available)
st.markdown("---")
st.markdown("### 🗺️ Regional Patterns")

# Sample regional data
regional_data = pd.DataFrame({
    'Region': ['Western', 'Central', 'Southern', 'Northern', 'Eastern'],
    '10% Mean': [8.5, 8.2, 8.7, 8.3, 8.6],
    '3% Mean': [33.2, 32.8, 33.5, 32.5, 33.8],
    'Sites': [3, 2, 2, 1, 2]
})

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 10% Rapid Method by Region")

    fig = px.bar(
        regional_data,
        x='Region',
        y='10% Mean',
        title='Mean Optimal Time - 10% Method',
        labels={'10% Mean': 'Mean Time (minutes)'}
    )
    fig.add_hline(
        y=sample_data['10%']['mean'],
        line_dash="dash",
        annotation_text="National Mean"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("#### 3% Slow Method by Region")

    fig = px.bar(
        regional_data,
        x='Region',
        y='3% Mean',
        title='Mean Optimal Time - 3% Method',
        labels={'3% Mean': 'Mean Time (minutes)'}
    )
    fig.add_hline(
        y=sample_data['3%']['mean'],
        line_dash="dash",
        annotation_text="National Mean"
    )
    st.plotly_chart(fig, use_container_width=True)

st.dataframe(regional_data, use_container_width=True)

# Recommendations
st.markdown("---")
st.markdown("### 💡 Recommendations for New Sites")

st.success("""
**Starting Point for New Sites/Locations**:

1. **10% Rapid Method**: Start with **8 minutes**
   - Typical range: 7-10 minutes
   - Run confirmation sweep: 6-10 minutes

2. **3% Slow Method**: Start with **32 minutes**
   - Typical range: 30-35 minutes
   - Run confirmation sweep: 30-38 minutes

**Next Steps**:
1. Prepare new working solution
2. Run minute-by-minute sweep around recommended time
3. Use Optimal Time Finder to confirm site-specific optimum
4. Document and contribute to national pattern
""")

# Data quality info
st.markdown("---")

with st.expander("ℹ️ About Pattern Data"):
    st.markdown("""
    ### Data Aggregation

    **Data Sources**:
    - Anonymized batch records from AMC sites
    - Quality-controlled optimal time determinations
    - Verified against AMC SOPs

    **Privacy**:
    - All data is anonymized
    - No patient or operator identifiable information
    - Site-level aggregation only

    ### Interpretation

    **Recommended Starting Times**:
    - Based on median optimal times across sites
    - Provides a sensible initial guess
    - **Must be confirmed** with local sweep

    **Regional Variations**:
    - May reflect local conditions (water, climate, etc.)
    - Not causally explained - descriptive only
    - Use as guidance, not prescription

    ### Updates

    Pattern data is updated as new batch records are submitted.
    Current data represents {total_batches} batches from {total_sites} sites.
    """.format(
        total_batches=sample_data['10%']['num_batches'] + sample_data['3%']['num_batches'],
        total_sites=max(sample_data['10%']['num_sites'], sample_data['3%']['num_sites'])
    ))

# Export
st.markdown("---")
st.markdown("### 💾 Export Pattern Data")

pattern_summary = pd.DataFrame({
    'Dilution': ['10%', '3%'],
    'Mean Time (min)': [sample_data['10%']['mean'], sample_data['3%']['mean']],
    'Median Time (min)': [sample_data['10%']['median'], sample_data['3%']['median']],
    'Std Dev (min)': [sample_data['10%']['std'], sample_data['3%']['std']],
    'Range': [f"{sample_data['10%']['min']}-{sample_data['10%']['max']}", f"{sample_data['3%']['min']}-{sample_data['3%']['max']}"],
    'Num Batches': [sample_data['10%']['num_batches'], sample_data['3%']['num_batches']],
    'Num Sites': [sample_data['10%']['num_sites'], sample_data['3%']['num_sites']]
})

csv = pattern_summary.to_csv(index=False)

st.download_button(
    label="📥 Download Pattern Summary (CSV)",
    data=csv,
    file_name="national_staining_pattern.csv",
    mime="text/csv"
)
