import pandas as pd
from nba_api.stats.endpoints import playercareerstats

def fetch_player_data(player_id):
    player_career = playercareerstats.PlayerCareerStats(player_id=player_id)
    player_career_df = player_career.get_data_frames()[0]
    return player_career_df

