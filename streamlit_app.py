import streamlit as st
import pandas as pd
from data.fetch_data import fetch_player_data
from data.process_data import calculate_average_points
from visualization.plot_data import plot_average_points

st.title('NBA Player Analysis')

player_options = {
    'LeBron James': '2544',
    'Stephen Curry': '201939',
    'Kevin Durant': '201142',
    'Giannis Antetokounmpo': '203507',
    'Klay Thompson': '202691',
    'Anthony Davis': '203076',
    'Russell Westbrook': '201566',
    'James Harden': '201935',
    'Chris Paul': '101108',
    'DeMar DeRozan': '201942'
}

selected_player = st.selectbox('Select a player', list(player_options.keys()))

if selected_player:
    player_id = player_options[selected_player]
    
    # Create two columns for layout
    col1, col2 = st.columns([1, 2])
    
    # Display player image in the first column
    with col1:
        image_url = f"https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/{player_id}.png"
        st.image(image_url, caption=selected_player, width=200)
    
    # Display stats and charts in the second column
    with col2:
        player_career_df = fetch_player_data(player_id)
        average_points = calculate_average_points(player_career_df)
        
        st.subheader('Career Stats')
        st.write(f"Average Points: {average_points.mean():.2f}")
        st.write(f"Highest Points per Season: {average_points.max():.2f}")
        st.write(f"Lowest Points per Season: {average_points.min():.2f}")

    # Display charts below the image and stats
    st.subheader('Average Points per Season')
    st.bar_chart(average_points)

    st.subheader('Detailed Visualization')
    fig = plot_average_points(average_points)
    st.pyplot(fig)
