"""
Chart Helpers for the Case Study Evaluation Hub.
Contains functions for creating various charts and visualizations.
"""

import plotly.express as px
import plotly.graph_objects as go
from typing import Dict

def create_donut_chart(data: Dict[str, int], names_label: str, values_label: str) -> go.Figure:
    """
    Create a donut chart from dictionary data.
    
    Args:
        data: Dictionary with categories and their counts
        names_label: Label for the categories
        values_label: Label for the values
    
    Returns:
        Plotly figure object
    """
    fig = px.pie(
        values=list(data.values()),
        names=list(data.keys()),
        hole=0.4,
        labels={
            'names': names_label,
            'values': values_label
        }
    )
    fig.update_traces(textposition='outside', textinfo='percent+label')
    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0)
    )
    return fig

def create_bar_chart(data: Dict[str, int], x_label: str, y_label: str) -> go.Figure:
    """
    Create a bar chart from dictionary data.
    
    Args:
        data: Dictionary with categories and their counts
        x_label: Label for x-axis
        y_label: Label for y-axis
    
    Returns:
        Plotly figure object
    """
    fig = px.bar(
        x=list(data.keys()),
        y=list(data.values()),
        labels={
            'x': x_label,
            'y': y_label
        }
    )
    fig.update_layout(
        margin=dict(t=0, b=0, l=0, r=0),
        xaxis_tickangle=-45
    )
    return fig 