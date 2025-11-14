"""
Batch Analysis Page

Compare and analyze optimal staining times across multiple batches and sites.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Batch Analysis", page_icon="📊", layout="wide")

# Page title
st.title("📊 Batch Analysis")
st.markdown("Compare optimal staining times across batches and sites")

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")

    analysis_type = st.selectbox(
        "Analysis Type",
        options=["Single Batch", "Multi-Batch Comparison", "Site-Level Analysis"]
    )

    dilution_filter = st.multiselect(
        "Filter by Dilution",
        options=["10%", "3%"],
        default=["10%", "3%"]
    )

    st.markdown("---")
    st.markdown("""
    ### 📋 CSV Format

    Required columns:
    - `batch_id`
    - `dilution` (10% or 3%)
    - `optimal_minute`
    - `pass_probability`
    - `mean_grade`

    Optional:
    - `site`
    - `date`
    - `technician`
    """)

# Main content
st.markdown("### 📤 Upload Batch Data")

uploaded_file = st.file_uploader(
    "Upload batch data CSV",
    type=['csv'],
    help="Upload CSV with batch optimal time records"
)

# Sample data button
if st.button("📝 Load Sample Data"):
    sample_data = {
        'batch_id': ['BATCH_001', 'BATCH_002', 'BATCH_003', 'BATCH_004', 'BATCH_005'],
        'site': ['AMC_HQ', 'AMC_HQ', 'Regional_A', 'Regional_B', 'Regional_A'],
        'dilution': ['10%', '3%', '10%', '10%', '3%'],
        'optimal_minute': [8, 32, 9, 7, 35],
        'pass_probability': [0.92, 0.88, 0.85, 0.90, 0.87],
        'mean_grade': [3.4, 3.2, 3.1, 3.5, 3.3],
        'date': pd.to_datetime(['2025-01-10', '2025-01-11', '2025-01-12', '2025-01-13', '2025-01-14'])
    }
    df = pd.DataFrame(sample_data)
    st.session_state['batch_data'] = df
    st.success("✅ Sample data loaded")

# Load data
df = None
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        st.session_state['batch_data'] = df
        st.success(f"✅ Loaded {len(df)} batch records")
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")

# Use session state data if available
if 'batch_data' in st.session_state:
    df = st.session_state['batch_data']

if df is not None:
    # Apply filters
    if dilution_filter:
        df = df[df['dilution'].isin(dilution_filter)]

    st.markdown("---")

    # Display data
    st.markdown("### 📋 Batch Records")

    st.dataframe(df, use_container_width=True)

    # Summary statistics
    st.markdown("### 📈 Summary Statistics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Batches", len(df))

    with col2:
        if 'site' in df.columns:
            st.metric("Unique Sites", df['site'].nunique())
        else:
            st.metric("Unique Sites", "N/A")

    with col3:
        st.metric("Avg Optimal Time", f"{df['optimal_minute'].mean():.1f} min")

    with col4:
        st.metric("Avg Pass Prob", f"{df['pass_probability'].mean():.1%}")

    # Analysis based on type
    st.markdown("---")

    if analysis_type == "Single Batch":
        st.markdown("### 🔍 Single Batch Details")

        selected_batch = st.selectbox("Select Batch", df['batch_id'].unique())

        batch_data = df[df['batch_id'] == selected_batch].iloc[0]

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Batch Information")
            st.info(f"""
            **Batch ID**: {batch_data['batch_id']}
            **Site**: {batch_data.get('site', 'N/A')}
            **Dilution**: {batch_data['dilution']}
            **Date**: {batch_data.get('date', 'N/A')}
            """)

        with col2:
            st.markdown("#### Optimal Time Results")
            st.success(f"""
            **Optimal Time**: {batch_data['optimal_minute']} minutes
            **Pass Probability**: {batch_data['pass_probability']:.1%}
            **Mean Grade**: {batch_data['mean_grade']:.1f}
            """)

    elif analysis_type == "Multi-Batch Comparison":
        st.markdown("### 📊 Multi-Batch Comparison")

        # Optimal time distribution
        fig = px.box(
            df,
            x='dilution',
            y='optimal_minute',
            color='dilution',
            title='Optimal Time Distribution by Dilution',
            labels={'optimal_minute': 'Optimal Time (minutes)', 'dilution': 'Dilution Method'}
        )
        st.plotly_chart(fig, use_container_width=True)

        # Time series if date available
        if 'date' in df.columns:
            st.markdown("#### Optimal Time Over Time")

            df_sorted = df.sort_values('date')

            fig = px.line(
                df_sorted,
                x='date',
                y='optimal_minute',
                color='dilution',
                markers=True,
                title='Optimal Time Trend Over Time',
                labels={'optimal_minute': 'Optimal Time (minutes)', 'date': 'Date'}
            )
            st.plotly_chart(fig, use_container_width=True)

        # Pass probability vs optimal time
        st.markdown("#### Pass Probability vs Optimal Time")

        fig = px.scatter(
            df,
            x='optimal_minute',
            y='pass_probability',
            color='dilution',
            size='mean_grade',
            hover_data=['batch_id'],
            title='Pass Probability vs Optimal Time',
            labels={
                'optimal_minute': 'Optimal Time (minutes)',
                'pass_probability': 'Pass Probability',
                'mean_grade': 'Mean Grade'
            }
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "Site-Level Analysis":
        if 'site' in df.columns:
            st.markdown("### 🏥 Site-Level Analysis")

            # Group by site and dilution
            site_summary = df.groupby(['site', 'dilution']).agg({
                'optimal_minute': ['mean', 'std', 'count'],
                'pass_probability': 'mean',
                'mean_grade': 'mean'
            }).reset_index()

            site_summary.columns = ['Site', 'Dilution', 'Mean Time', 'Std Time', 'Batch Count', 'Avg Pass Prob', 'Avg Grade']

            st.dataframe(site_summary, use_container_width=True)

            # Site comparison chart
            fig = px.bar(
                df,
                x='site',
                y='optimal_minute',
                color='dilution',
                barmode='group',
                title='Optimal Time by Site and Dilution',
                labels={'optimal_minute': 'Optimal Time (minutes)', 'site': 'Site'}
            )
            st.plotly_chart(fig, use_container_width=True)

            # Variability within sites
            st.markdown("#### Site Variability")

            fig = px.box(
                df,
                x='site',
                y='optimal_minute',
                color='dilution',
                title='Optimal Time Variability by Site',
                labels={'optimal_minute': 'Optimal Time (minutes)', 'site': 'Site'}
            )
            st.plotly_chart(fig, use_container_width=True)

        else:
            st.warning("Site column not found in data. Upload data with 'site' column for site-level analysis.")

    # Export
    st.markdown("---")
    st.markdown("### 💾 Export Analysis")

    if st.button("📥 Download Filtered Data (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

else:
    st.info("👆 Upload batch data CSV or load sample data to begin analysis")

# Tips
st.markdown("---")

with st.expander("💡 Tips for Batch Analysis"):
    st.markdown("""
    ### CSV Format

    Create a CSV file with the following columns:

    ```csv
    batch_id,site,dilution,optimal_minute,pass_probability,mean_grade,date
    BATCH_001,AMC_HQ,10%,8,0.92,3.4,2025-01-10
    BATCH_002,AMC_HQ,3%,32,0.88,3.2,2025-01-11
    ```

    ### Interpretation

    **Multi-Batch Comparison**:
    - Compare optimal times across batches
    - Identify trends over time
    - Spot outliers or inconsistencies

    **Site-Level Analysis**:
    - Compare performance across sites
    - Identify sites needing support
    - Track variability within sites

    ### Quality Control

    - **High Variability**: May indicate inconsistent protocols
    - **Outliers**: Investigate batch-specific issues
    - **Trends**: Monitor for drift in staining behavior
    """)
