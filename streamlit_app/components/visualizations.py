"""
Visualization Components

Reusable visualization components for Streamlit app.

@author: Sayumi Devasurendra
@version: 0.1.0
"""

import plotly.graph_objects as go
import plotly.express as px
import numpy as np


def create_grade_bar_chart(probabilities: np.ndarray, grade_labels: list = None):
    """
    Create bar chart for grade probabilities

    Args:
        probabilities: Array of probabilities for each grade
        grade_labels: List of grade labels (default: I-V)

    Returns:
        Plotly figure
    """
    if grade_labels is None:
        grade_labels = ['I', 'II', 'III', 'IV', 'V']

    fig = go.Figure(data=[
        go.Bar(
            x=grade_labels,
            y=probabilities,
            marker_color=['green' if p >= 0.3 else 'lightblue' for p in probabilities],
            text=[f'{p:.1%}' for p in probabilities],
            textposition='auto'
        )
    ])

    fig.update_layout(
        title='Grade Probability Distribution',
        xaxis_title='Grade',
        yaxis_title='Probability',
        yaxis_range=[0, 1],
        showlegend=False,
        height=400
    )

    return fig


def create_time_sweep_plot(minutes: list, pass_probs: list, confidence_threshold: float = 0.8, optimal_minute: int = None):
    """
    Create line plot for time sweep analysis

    Args:
        minutes: List of staining times
        pass_probs: List of pass probabilities
        confidence_threshold: Threshold for passing
        optimal_minute: Optimal minute to mark (optional)

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Pass probability line
    fig.add_trace(go.Scatter(
        x=minutes,
        y=pass_probs,
        mode='lines+markers',
        name='Pass Probability',
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))

    # Threshold line
    fig.add_hline(
        y=confidence_threshold,
        line_dash='dash',
        line_color='red',
        annotation_text=f'Pass Threshold ({confidence_threshold:.0%})',
        annotation_position='right'
    )

    # Mark optimal minute
    if optimal_minute is not None:
        fig.add_vline(
            x=optimal_minute,
            line_dash='dot',
            line_color='green',
            annotation_text=f'Optimal: {optimal_minute} min',
            annotation_position='top'
        )

    fig.update_layout(
        title='Pass Probability vs Staining Time',
        xaxis_title='Staining Time (minutes)',
        yaxis_title='Pass Probability',
        yaxis_range=[0, 1],
        hovermode='x unified',
        height=500
    )

    return fig


def create_batch_comparison_plot(df, x_col: str, y_col: str, color_col: str = None, title: str = ''):
    """
    Create comparison plot for batch data

    Args:
        df: DataFrame with batch data
        x_col: Column for x-axis
        y_col: Column for y-axis
        color_col: Column for color grouping
        title: Plot title

    Returns:
        Plotly figure
    """
    if color_col:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            color=color_col,
            title=title,
            hover_data=df.columns
        )
    else:
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            title=title,
            hover_data=df.columns
        )

    fig.update_layout(height=500)

    return fig


def create_failure_reason_chart(reasons: dict):
    """
    Create horizontal bar chart for failure reasons

    Args:
        reasons: Dictionary of {reason: count}

    Returns:
        Plotly figure
    """
    fig = go.Figure(data=[
        go.Bar(
            y=list(reasons.keys()),
            x=list(reasons.values()),
            orientation='h',
            marker_color='coral',
            text=list(reasons.values()),
            textposition='auto'
        )
    ])

    fig.update_layout(
        title='Failure Reasons Distribution',
        xaxis_title='Count',
        yaxis_title='Reason',
        height=max(300, len(reasons) * 50),
        showlegend=False
    )

    return fig
