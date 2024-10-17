# NBA Analysis

A simple Python app that demonstrates some fundamental data analysis practices for NBA player statistics. This project is a work-in-progress, open to suggestions, and serves as a portfolio repository!

## Features

- Fetch NBA player data using the `nba_api`
- Process and analyze player statistics (currently only Points per Season)
- Visualize player performance using Matplotlib and Seaborn (Limited players)
- Interactive web applications using Dash and Streamlit (Streamlit preferred for easier and nicer look)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/gshantanu15/nba_analysis.git
   cd nba_analysis
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Dash Application
I do not recommend using Dash in this project as I have not configured it yet, or explored enough. Streamlit is recommended! ´:D´

### Streamlit Application

To run the Streamlit application:

```
streamlit run streamlit_app.py
```

This will open a new tab in your default web browser with the Streamlit app.

## Initial Commit
- .gitignore : Using GitHub's template for a python project
- LICENSE : Using MIT License intially, as it seemed easiest. May change later, if needed.
- README.md : Markdown file! (What you're reading rn :D)

## Project Structure

- `app.py`: Dash application
- `streamlit_app.py`: Streamlit application
- `data/`: Module for data fetching and processing
- `visualization/`: Module for data visualization
- `requirements.txt`: List of Python dependencies

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- NBA API for providing access to NBA statistics and headshots of players
- Dash and Streamlit for enabling interactive web applications
- Pandas, Matplotlib, and Seaborn for data processing and visualization