# This module contains functions for processing NBA player data
import pandas as pd

def calculate_average_points(player_career_df):
    if not isinstance(player_career_df, pd.DataFrame):
        raise ValueError("Input must be a pandas DataFrame")
    
    if 'SEASON_ID' not in player_career_df.columns or 'PTS' not in player_career_df.columns:
        raise ValueError("DataFrame must contain 'SEASON_ID' and 'PTS' columns")
    
    average_points = player_career_df.groupby('SEASON_ID')['PTS'].mean()
    return average_points
