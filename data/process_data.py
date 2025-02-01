# This module contains functions for processing NBA player data
import pandas as pd
import numpy as np
from datetime import datetime

def calculate_average_points(player_career_df):
    if not isinstance(player_career_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if 'SEASON_ID' not in player_career_df.columns or 'PTS' not in player_career_df.columns:
        raise ValueError("DataFrame must contain 'SEASON_ID' and 'PTS' columns")
    
    average_points = player_career_df.groupby('SEASON_ID')['PTS'].mean()
    return average_points

def handle_missing_game_stats(df):
    """Handle missing values for game-related statistics"""
    # If GP (Games Played) is 0 or missing, set game stats to 0
    game_stats = ['PTS', 'AST', 'REB', 'MIN']
    gp_zero_mask = (df['GP'] == 0) | df['GP'].isna()
    df.loc[gp_zero_mask, game_stats] = 0
    return df

def handle_missing_efficiency_stats(df):
    """Handle missing values for efficiency-related statistics"""
    # For efficiency stats, use position-based median imputation
    efficiency_stats = ['PLAYER_EFFICIENCY_RATING']
    for stat in efficiency_stats:
        if stat in df.columns:
            pos_medians = df.groupby('POSITION')[stat].transform('median')
            df[stat].fillna(pos_medians, inplace=True)
            # Add missing indicator
            df[f'{stat}_WAS_MISSING'] = df[stat].isna().astype(int)
    return df

def process_longevity_features(career_df):
    """
    Process and create features for career longevity prediction.
    
    Parameters:
    -----------
    career_df : pandas DataFrame
        Player career data including stats and biographical info
    
    Returns:
    --------
    pandas DataFrame
        Processed DataFrame with additional features for longevity prediction
    """
    if not isinstance(career_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    required_cols = ['SEASON_ID', 'PTS', 'AST', 'REB', 'GP', 'MIN']
    # Check if any required columns are missing
    missing_cols = []
    for col in required_cols:
        if col not in career_df.columns:
            missing_cols.append(col)
    if missing_cols:
        raise ValueError(f"The following required columns are missing: {missing_cols}")
    
    # Create a copy to avoid modifying the original
    df = career_df.copy()
    
    # Handle missing values for different types of statistics
    df = handle_missing_game_stats(df)
    
    # Create career progression features
    df['SEASON_YEAR'] = df['SEASON_ID'].str[:4].astype(int)
    df['CAREER_YEAR'] = df.groupby('PLAYER_ID')['SEASON_YEAR'].rank(method='dense')
    
    # Calculate minutes per game and games played ratio FIRST
    df['MIN_PER_GAME'] = df['MIN'] / df.apply(lambda x: max(x['GP'], 1), axis=1)  # Avoid division by zero
    df['GP_RATIO'] = df['GP'] / 82  # 82 is a full NBA season
    
    # Calculate rolling averages with weighted windows (last 3 seasons)
    rolling_stats = ['PTS', 'AST', 'REB', 'MIN_PER_GAME', 'PLAYER_EFFICIENCY_RATING', 'GP']
    for stat in rolling_stats:
        # Calculate percentage change for each stat
        df[f'{stat}_PCT_CHANGE'] = df.groupby('PLAYER_ID')[stat].pct_change()
        
        # Calculate 3-season weighted rolling average (50% current, 30% previous, 20% two seasons ago)
        df[f'{stat}_ROLLING_AVG'] = df.groupby('PLAYER_ID')[stat].transform(
            lambda x: x.fillna(method='ffill').rolling(window=3, min_periods=1).apply(
                lambda window: np.average(window, weights=[0.5, 0.3, 0.2][:len(window)])
            )
        )
        
        # Calculate rolling decline percentage (negative values indicate decline)
        df[f'{stat}_ROLLING_DECLINE'] = df.groupby('PLAYER_ID')[f'{stat}_ROLLING_AVG'].pct_change()
    
    # Create magnitude-sensitive decline indicators
    df['PER_DECLINE_SEVERITY'] = df['PLAYER_EFFICIENCY_RATING_PCT_CHANGE'].apply(
        lambda x: abs(min(x, 0))  # Convert declines to positive values, no decline = 0
    )
    
    df['USAGE_DECLINE_SEVERITY'] = df['MIN_PER_GAME_PCT_CHANGE'].apply(
        lambda x: abs(min(x, 0))  # Convert declines to positive values, no decline = 0
    )
    
    # Calculate cumulative decline over last 3 seasons
    df['PER_3YEAR_DECLINE'] = df.groupby('PLAYER_ID')['PER_DECLINE_SEVERITY'].transform(
        lambda x: x.rolling(window=3, min_periods=1).sum()
    )
    
    df['USAGE_3YEAR_DECLINE'] = df.groupby('PLAYER_ID')['USAGE_DECLINE_SEVERITY'].transform(
        lambda x: x.rolling(window=3, min_periods=1).sum()
    )
    
    # Handle efficiency stats after basic stats are processed
    df = handle_missing_efficiency_stats(df)
    
    # Handle missing draft year with median imputation
    if 'DRAFT_YEAR' in df.columns:
        df['DRAFT_YEAR'] = pd.to_numeric(df['DRAFT_YEAR'], errors='coerce')
        df['DRAFT_YEAR'].fillna(df['DRAFT_YEAR'].median(), inplace=True)
    else:
        # Estimate from first season if not available
        first_season = df['SEASON_ID'].min()
        df['DRAFT_YEAR'] = int(first_season[:4])
    
    # Calculate age from draft year (approximate)
    current_year = datetime.now().year
    df['YEARS_FROM_DRAFT'] = current_year - df['DRAFT_YEAR'].astype(float)
    
    # Create performance decline indicators with proper handling of missing values
    df['PER_DECLINE'] = df.groupby('PLAYER_ID')['PLAYER_EFFICIENCY_RATING'].transform(
        lambda x: x.fillna(method='ffill').diff() < 0
    ).fillna(False)
    
    df['USAGE_DECLINE'] = df.groupby('PLAYER_ID')['MIN_PER_GAME'].transform(
        lambda x: x.fillna(method='ffill').diff() < 0
    ).fillna(False)
    
    # Add missing value indicators for key metrics
    key_metrics = ['PLAYER_EFFICIENCY_RATING', 'MIN_PER_GAME', 'GP']
    for metric in key_metrics:
        df[f'{metric}_MISSING'] = df[metric].isna().astype(int)
    
    # Final safety net: fill any remaining missing numeric values with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    
    return df

def calculate_career_risk_score(processed_df):
    """
    Calculate a risk score for career ending based on various factors.
    Higher score indicates higher risk of career end.
    
    Parameters:
    -----------
    processed_df : pandas DataFrame
        Processed player data with longevity features
    
    Returns:
    --------
    float
        Risk score between 0 and 100
    """
    # Weight factors that contribute to career risk
    weights = {
        'AGE_FACTOR': 0.30,
        'PERFORMANCE_DECLINE': 0.30,
        'USAGE_DECLINE': 0.28,
        'INJURY_RISK': 0.12          
    }
    
    # Get the most recent season's data for current risk assessment
    latest_season = processed_df.sort_values('SEASON_YEAR', ascending=False).iloc[0]
    
    # Age factor (higher risk with age)
    age_risk = np.clip(latest_season['YEARS_FROM_DRAFT'] / 20, 0, 1)
    
    # Performance decline risk (use rolling and magnitude-sensitive metrics)
    perf_decline_short = latest_season['PER_DECLINE_SEVERITY']  # Recent decline
    perf_decline_long = latest_season['PER_3YEAR_DECLINE']     # Cumulative 3-year decline
    perf_risk = np.clip((0.7 * perf_decline_short + 0.3 * perf_decline_long), 0, 1)
    
    # Usage decline risk (use rolling and magnitude-sensitive metrics)
    usage_decline_short = latest_season['USAGE_DECLINE_SEVERITY']  # Recent decline
    usage_decline_long = latest_season['USAGE_3YEAR_DECLINE']     # Cumulative 3-year decline
    usage_risk = np.clip((0.7 * usage_decline_short + 0.3 * usage_decline_long), 0, 1)
    
    # Calculate injury risk with historical context
    recent_gp_ratio = latest_season['GP_RATIO']
    gp_trend = latest_season.get('GP_PCT_CHANGE', 0)  # Changed from GP_ROLLING_DECLINE to GP_PCT_CHANGE
    injury_risk = np.clip(
        (1 - recent_gp_ratio) * 1.5 +  # Recent missed games
        max(gp_trend, 0) + 
        (processed_df['GP_RATIO'].std() * 2),  # Volatility in availability
        0, 1
    )
    
    # Calculate weighted risk score
    risk_score = (
        weights['AGE_FACTOR'] * age_risk +
        weights['PERFORMANCE_DECLINE'] * perf_risk +
        weights['USAGE_DECLINE'] * usage_risk +
        weights['INJURY_RISK'] * injury_risk
    )
    
    return float(np.clip(risk_score * 100, 0, 100))  # Return as percentage
