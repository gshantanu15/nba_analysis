import streamlit as st
import pandas as pd
from data.fetch_data import fetch_player_data, fetch_longevity_data, load_image, fetch_all_players
from data.process_data import calculate_average_points, process_longevity_features, calculate_career_risk_score
from visualization.plot_data import plot_average_points, plot_longevity_analysis, plot_risk_score_gauge

# Add custom CSS to make the content wider
st.markdown("""
<style>
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title('NBA Player Analysis Dashboard')

# Sidebar for player selection
st.sidebar.title('Player Selection')

# Fetch list of all players
players_df = fetch_all_players()

if not players_df.empty:
    # Create player selection dropdown with additional info
    players_df['DISPLAY_NAME'] = players_df.apply(
        lambda x: f"{x['PLAYER_NAME']} ({x['TEAM_ABBREVIATION']} {x['FROM_YEAR']}-{x['TO_YEAR']})", 
        axis=1
    )
    
    # Default to Karl-Anthony Towns
    default_idx = players_df[players_df['PLAYER_ID'] == '203999'].index[0] if '203999' in players_df['PLAYER_ID'].values else 0
    
    selected_player = st.sidebar.selectbox(
        'Select Player',
        options=players_df['DISPLAY_NAME'].tolist(),
        index=default_idx
    )
    
    # Extract player ID from selection
    selected_name = selected_player.split(' (')[0]  # Remove team and years info
    player_id = players_df[players_df['PLAYER_NAME'] == selected_name]['PLAYER_ID'].iloc[0]
    
    # Main content
    if player_id:
        # Fetch player data
        player_data = fetch_player_data(player_id)
        
        # Basic stats section
        st.header('Basic Career Statistics')
        
        # Create columns for image and stats
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Display player image
            image_url = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
            with st.spinner("Loading player image..."):
                img = load_image(image_url)
            if img is not None:
                st.image(img, caption=selected_name, width=200)
            else:
                st.warning("Failed to load player image.")
        
        with col2:
            avg_points = calculate_average_points(player_data)
            st.plotly_chart(plot_average_points(avg_points, selected_name))
        
        # Career Longevity Analysis section
        st.header('Career Longevity Analysis')
        
        with st.spinner('Analyzing career longevity...'):
            # Fetch comprehensive data for longevity analysis
            longevity_data = fetch_longevity_data(player_id)
            
            # Process features for longevity prediction
            processed_data = process_longevity_features(longevity_data)
            
            # Calculate risk score
            risk_score = calculate_career_risk_score(processed_data)
            
            # Display risk score gauge
            st.subheader('Career Risk Assessment')
            st.plotly_chart(plot_risk_score_gauge(risk_score))
            
            # Display detailed analysis
            figures = plot_longevity_analysis(processed_data)
            
            # Career trajectory
            st.subheader('Career Performance Trajectory')
            st.plotly_chart(figures['trajectory'])
            
            # Risk factors analysis
            col1, col2 = st.columns(2)
            with col1:
                st.subheader('Risk Factors Breakdown')
                st.plotly_chart(figures['risk_radar'])
            
            with col2:
                st.subheader('Efficiency Trend')
                st.plotly_chart(figures['efficiency'])
            
            # Usage analysis
            st.subheader('Playing Time Trend')
            st.plotly_chart(figures['usage'])
            
            # Key insights
            st.subheader('Key Insights')
            
            # Calculate some basic insights
            recent_per = processed_data['PLAYER_EFFICIENCY_RATING'].iloc[-1]
            career_avg_per = processed_data['PLAYER_EFFICIENCY_RATING'].mean()
            recent_mins = processed_data['MIN_PER_GAME'].iloc[-1]
            career_avg_mins = processed_data['MIN_PER_GAME'].mean()
            
            insights = []
            
            if recent_per < career_avg_per:
                insights.append("⚠️ Recent efficiency is below career average")
            else:
                insights.append("✅ Maintaining efficiency above career average")
                
            if recent_mins < career_avg_mins * 0.8:
                insights.append("⚠️ Significant decrease in playing time")
            elif recent_mins > career_avg_mins * 1.1:
                insights.append("📈 Increased role in team rotation")
            
            if risk_score > 70:
                insights.append("🚨 High risk of career decline")
            elif risk_score > 40:
                insights.append("⚠️ Moderate risk of career decline")
            else:
                insights.append("✅ Low risk of career decline")
            
            for insight in insights:
                st.markdown(f"- {insight}")
else:
    st.error('Unable to load player list. Please try again later.')
