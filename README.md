# NBA Player Career Analysis Dashboard

A Python application for analyzing NBA players' career trajectories and predicting career longevity risks. This project combines statistical analysis with interactive visualizations to provide insights into player performance and career sustainability.

## Features

### Player Analysis
- **Career Statistics Visualization**
  - Points per season analysis
  - Career trajectory tracking
  - Performance metrics over time
  - Interactive data visualization

### Career Longevity Analysis
- **Risk Assessment**
  - Career risk score calculation
  - Performance decline analysis
  - Usage pattern tracking
  - Injury risk evaluation

### Interactive Dashboard
- **Player Selection**
  - Comprehensive player database
  - Search by player name
  - Team and career span information
  - Player head-shots integration

- **Visual Analytics**
  - Career performance trajectory
  - Risk factor radar charts
  - Efficiency trend analysis
  - Playing time patterns

## Technical Implementation

### Data Processing
- **Advanced Metrics**
  - Rolling averages with weighted windows
  - Magnitude-sensitive decline indicators
  - Cumulative decline tracking
  - Performance efficiency ratings

- **Risk Calculation**
  - Multi-factor risk assessment
  - Age-adjusted analysis
  - Performance trend evaluation
  - Injury history consideration

### Visualization Components
- **Interactive Charts**
  - Plotly for dynamic visualizations
  - Streamlit for web interface
  - Real-time data updates
  - Responsive design

## Installation

1. Clone the repository:
```bash
git clone https://github.com/gshantanu15/nba_analysis.git
cd nba_analysis
```

2. Create and activate a virtual environment (recommended):
```bash
python -m venv nba_env
source nba_env/bin/activate  # On Windows: nba_env\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Launch the Streamlit dashboard:
```bash
streamlit run streamlit_app.py
```

The application will open in your default web browser, featuring:
- Player selection dropdown with team information
- Career statistics visualization
- Longevity risk analysis
- Performance insights

## Project Structure

```
nba_analysis/
├── data/
│   ├── fetch_data.py      # NBA API integration
│   └── process_data.py    # Data processing and analysis
├── visualization/
│   └── plot_data.py       # Visualization functions
├── streamlit_app.py       # Main application
└── requirements.txt       # Dependencies
```

### Key Components

#### Data Module
- `fetch_data.py`: Handles NBA API integration and data retrieval
- `process_data.py`: Implements advanced statistical analysis and risk calculations

#### Visualization Module
- `plot_data.py`: Creates interactive charts and visualizations
- Utilizes Plotly for dynamic data representation

#### Main Application
- `streamlit_app.py`: Integrates all components into an interactive dashboard

## Dependencies

- `streamlit`: Web application framework
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `plotly`: Interactive visualizations
- `nba_api`: NBA statistics and data
- `Pillow`: Image processing

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NBA API for providing comprehensive basketball statistics
- Streamlit team for the excellent web framework
- Contributors and users of this project