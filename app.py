import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from data.fetch_data import fetch_player_data
from data.process_data import calculate_average_points
from visualization.plot_data import plot_average_points

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1('NBA Player Analysis'),
    dcc.Dropdown(
        id='player-dropdown',
        options=[
            {'label': 'LeBron James', 'value': '2544'},
            # to add more players as needed
        ],
        value='2544'
    ),
    dcc.Graph(id='points-graph')
])

# Define the callback to update the graph
@app.callback(
    Output('points-graph', 'figure'),
    [Input('player-dropdown', 'value')]
)
def update_graph(player_id):
    player_career_df = fetch_player_data(player_id)
    average_points = calculate_average_points(player_career_df)

    fig = {
        'data': [
            {'x': average_points.index, 'y': average_points.values, 'type': 'bar'}
        ],
        'layout': {
            'title': 'Average Points per Season'
        }
    }
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
