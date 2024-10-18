import pandas as pd
from nba_api.stats.endpoints import playercareerstats
import requests
from io import BytesIO
from PIL import Image
import streamlit as st

def fetch_player_data(player_id):
    player_career = playercareerstats.PlayerCareerStats(player_id=player_id)
    player_career_df = player_career.get_data_frames()[0]
    return player_career_df

@st.cache_data
def load_image(url):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content))
        return img
    except:
        return None