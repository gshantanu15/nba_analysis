# This module contains functions for plotting NBA player data
# It uses matplotlib and seaborn for data visualization
import matplotlib.pyplot as plt
import seaborn as sns

def plot_average_points(average_points):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.lineplot(x=average_points.index, y=average_points.values, ax=ax, marker='o')
    plt.title('Average Points per Season')
    plt.xlabel('Season')
    plt.ylabel('Average Points')
    plt.xticks(rotation=45)
    return fig
