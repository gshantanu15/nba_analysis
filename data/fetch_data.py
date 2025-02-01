import pandas as pd
from nba_api.stats.endpoints import playercareerstats, commonplayerinfo, playerprofilev2, playerindex
import requests
from io import BytesIO
from PIL import Image
import streamlit as st
import numpy as np

def calculate_per(row):
    """
    Calculate a simplified version of Player Efficiency Rating (PER)
    This is a basic approximation as the actual formula is quite complex
    """
    try:
        # Basic positive contributions
        pos_factor = (
            row['PTS'] + 
            row['REB'] * 1.2 + 
            row['AST'] * 1.5 + 
            row['STL'] * 2.0 + 
            row['BLK'] * 2.0
        )
        
        # Basic negative contributions
        neg_factor = (
            row['FGA'] - row['FGM'] + 
            (row['FTA'] - row['FTM']) * 0.5 + 
            row['TOV'] * 1.0
        )
        
        # Calculate per minute and adjust for position
        minutes_factor = row['MIN'] if row['MIN'] > 0 else 1
        raw_per = (pos_factor - neg_factor) * (48.0 / minutes_factor)
        
        # League average PER is calibrated to 15
        return raw_per * (15.0 / 13.0)  # Rough adjustment to match league average
    except:
        return None

def fetch_player_data(player_id):
    """
    Fetch basic player career data and info.
    
    Parameters:
    -----------
    player_id : str
        NBA player ID
        
    Returns:
    --------
    pandas DataFrame
        Player career statistics with basic info
    """
    # Get career stats
    player_career = playercareerstats.PlayerCareerStats(player_id=player_id)
    player_career_df = player_career.get_data_frames()[0]
    
    # Get player info for name
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    player_info_df = player_info.get_data_frames()[0]
    
    # Add player name to career stats
    player_career_df['PLAYER_NAME'] = player_info_df['DISPLAY_FIRST_LAST'].iloc[0]
    
    return player_career_df

@st.cache_data
def fetch_longevity_data(player_id):
    """
    Fetch comprehensive player data for career longevity prediction.
    Includes career stats, biographical info, and advanced metrics.
    """
    # Basic career stats
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career_stats.get_data_frames()[0]
    
    # Player biographical info
    player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
    bio_df = player_info.get_data_frames()[0]
    
    # Advanced career metrics
    profile = playerprofilev2.PlayerProfileV2(player_id=player_id)
    advanced_df = profile.season_totals_regular_season.get_data_frame()
    
    # Map the column names to our expected format
    column_mapping = {
        'SEASON_ID': 'SEASON_ID',
        'PER': 'PLAYER_EFFICIENCY_RATING',
        'GP': 'GP',
        'MIN': 'MIN'
    }
    
    # Select and rename columns that exist
    available_columns = []
    rename_dict = {}
    for target_col, api_col in column_mapping.items():
        if api_col in advanced_df.columns:
            available_columns.append(api_col)
            if target_col != api_col:
                rename_dict[api_col] = target_col
    
    # Select available columns and rename if needed
    advanced_df = advanced_df[available_columns].rename(columns=rename_dict)
    
    # Merge with career_df, using outer join to keep all seasons
    career_df = career_df.merge(
        advanced_df,
        on='SEASON_ID',
        how='outer',
        suffixes=('', '_advanced')
    )
    
    # Calculate PER if it's not available
    if 'PLAYER_EFFICIENCY_RATING' not in career_df.columns:
        st.warning("Player Efficiency Rating not available from API, calculating approximation...")
        career_df['PLAYER_EFFICIENCY_RATING'] = career_df.apply(calculate_per, axis=1)
        # Fill any remaining NaN values with league average PER (15.0)
        career_df['PLAYER_EFFICIENCY_RATING'].fillna(15.0, inplace=True)
    
    # Add biographical features, handling potential missing columns
    bio_features = {
        'DRAFT_YEAR': 'DRAFT_YEAR',
        'DRAFT_ROUND': 'DRAFT_ROUND',
        'DRAFT_NUMBER': 'DRAFT_NUMBER',
        'HEIGHT': 'HEIGHT',
        'WEIGHT': 'WEIGHT',
        'POSITION': 'POSITION'
    }
    
    for target_col, bio_col in bio_features.items():
        if bio_col in bio_df.columns:
            if target_col == 'DRAFT_YEAR':
                # Ensure DRAFT_YEAR is numeric
                try:
                    career_df[target_col] = pd.to_numeric(bio_df[bio_col].iloc[0], errors='coerce')
                except:
                    # If conversion fails, estimate from first season
                    first_season = career_df['SEASON_ID'].min()
                    career_df[target_col] = int(first_season[:4])
            else:
                career_df[target_col] = bio_df[bio_col].iloc[0]
        else:
            # Provide default values for missing biographical data
            if target_col == 'DRAFT_YEAR':
                # Estimate draft year from first season
                first_season = career_df['SEASON_ID'].min()
                career_df[target_col] = pd.to_numeric(first_season[:4], errors='coerce')
            elif target_col == 'POSITION':
                career_df[target_col] = 'Unknown'
            else:
                career_df[target_col] = None
    
    # Ensure DRAFT_YEAR is numeric for calculations
    career_df['DRAFT_YEAR'] = pd.to_numeric(career_df['DRAFT_YEAR'], errors='coerce')
    if career_df['DRAFT_YEAR'].isna().any():
        # If any conversion failed, fill with estimated year from first season
        first_season = career_df['SEASON_ID'].min()
        career_df['DRAFT_YEAR'].fillna(int(first_season[:4]), inplace=True)
    
    return career_df

@st.cache_data
def load_image(url):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None

@st.cache_data
def fetch_all_players():
    """
    Fetch list of all NBA players.
    
    Returns:
    --------
    pandas DataFrame
        DataFrame containing player names and IDs
    """
    try:
        # Use playerindex endpoint to get all players
        players = playerindex.PlayerIndex()
        players_df = players.get_data_frames()[0]
        
        # Create full name and keep only active players
        players_df['PLAYER_NAME'] = players_df['PLAYER_FIRST_NAME'] + ' ' + players_df['PLAYER_LAST_NAME']
        
        # Sort by name for better display
        players_df = players_df.sort_values('PLAYER_NAME')
        
        # Keep only necessary columns
        return players_df[['PERSON_ID', 'PLAYER_NAME', 'TEAM_ABBREVIATION', 'FROM_YEAR', 'TO_YEAR']].rename(
            columns={'PERSON_ID': 'PLAYER_ID'}
        )
    except Exception as e:
        st.error(f"Error fetching player list: {str(e)}")
        return pd.DataFrame()