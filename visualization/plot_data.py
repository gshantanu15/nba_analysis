# This module contains functions for plotting NBA player data
# It uses matplotlib and seaborn for data visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def plot_average_points(average_points, player_name):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=average_points.index, y=average_points.values, ax=ax, marker='o')
    plt.title(f'Average Points per Season - {player_name}')
    plt.xlabel('Season')
    plt.ylabel('Average Points')
    plt.xticks(rotation=45)
    return fig

def plot_career_trajectory(player_data):
    """Plot player's career statistics over time"""
    fig = px.line(player_data, x='SEASON_ID', y='PTS', title='Career Points Progression')
    return fig

def plot_longevity_analysis(processed_df):
    """
    Create visualizations for career longevity analysis.
    
    Parameters:
    -----------
    processed_df : pandas DataFrame
        Processed player data with longevity features
    
    Returns:
    --------
    dict
        Dictionary containing multiple plotly figures for different aspects of longevity analysis
    """
    figures = {}
    
    # Career trajectory plot
    trajectory_fig = go.Figure()
    metrics = ['PTS_ROLLING_AVG', 'AST_ROLLING_AVG', 'REB_ROLLING_AVG']
    colors = ['blue', 'red', 'green']
    
    for metric, color in zip(metrics, colors):
        trajectory_fig.add_trace(
            go.Scatter(
                x=processed_df['CAREER_YEAR'],
                y=processed_df[metric],
                name=metric.replace('_ROLLING_AVG', ''),
                line=dict(color=color)
            )
        )
    
    trajectory_fig.update_layout(
        title='Career Performance Trajectory',
        xaxis_title='Years in League',
        yaxis_title='Statistics (3-Season Rolling Average)',
        hovermode='x unified'
    )
    figures['trajectory'] = trajectory_fig
    
    # Risk factors radar chart
    risk_factors = {
        'Age Risk': np.clip(processed_df['YEARS_FROM_DRAFT'].iloc[-1] / 20, 0, 1),
        'Performance Decline': processed_df['PER_DECLINE_SEVERITY'].mean(),
        'Usage Decline': processed_df['USAGE_DECLINE_SEVERITY'].mean(),
        'Injury Risk': 1 - processed_df['GP_RATIO'].mean()
    }
    
    radar_fig = go.Figure()
    radar_fig.add_trace(go.Scatterpolar(
        r=list(risk_factors.values()),
        theta=list(risk_factors.keys()),
        fill='toself',
        name='Risk Factors'
    ))
    
    radar_fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False,
        title='Career Risk Factors Analysis'
    )
    figures['risk_radar'] = radar_fig
    
    # Efficiency trend
    efficiency_fig = px.line(
        processed_df,
        x='CAREER_YEAR',
        y='PLAYER_EFFICIENCY_RATING',
        title='Player Efficiency Rating Trend'
    )
    efficiency_fig.add_hline(
        y=processed_df['PLAYER_EFFICIENCY_RATING'].mean(),
        line_dash="dash",
        annotation_text="Career Average"
    )
    figures['efficiency'] = efficiency_fig
    
    # Usage trend
    usage_fig = px.line(
        processed_df,
        x='CAREER_YEAR',
        y='MIN_PER_GAME',
        title='Minutes Per Game Trend'
    )
    usage_fig.add_hline(
        y=processed_df['MIN_PER_GAME'].mean(),
        line_dash="dash",
        annotation_text="Career Average"
    )
    figures['usage'] = usage_fig
    
    return figures

def plot_risk_score_gauge(risk_score):
    """
    Create a gauge chart for the career risk score.
    
    Parameters:
    -----------
    risk_score : float
        Career risk score between 0 and 100
    
    Returns:
    --------
    plotly.graph_objects.Figure
        Gauge chart figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=float(risk_score),  # Ensure single float value
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Career Risk Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "lightgreen"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': float(risk_score)  # Ensure single float value
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=50, b=10),
        font={'size': 16}
    )
    
    return fig
