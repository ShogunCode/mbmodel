import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import numpy as np
from io import BytesIO
import pandas as pd
import base64
from .model import make_predictions
import logging

# def handle_confidence_plot(confidence_scores, H, cluster_labels):
#     # Generate plots
#     plot_path = generate_confidence_plot(H, cluster_labels, confidence_scores)  # Implement generate_plots
#     # Encode plot for web display
#     encoded_plot = encode_plot_for_web(plot_path)  # Implement encode_plot_for_web
#     return encoded_plot

def compute_confidence_intervals(data):
    if data.ndim > 1:
        raise ValueError("Data must be 1-dimensional to compute confidence intervals")

    mean_data = np.mean(data)
    stats = [np.mean(np.random.choice(data, len(data), replace=True)) for _ in range(1000)]
    lower = np.percentile(stats, 2.5)
    upper = np.percentile(stats, 97.5)
    return (mean_data, lower, upper)

def analyze_data(data, labels, confidence_scores):
    class_labels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'NC']
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'grey']

    data_list, intervals, plotted_labels, positions, color_assignment = [], [], [], [], []
    base_position = 1
    tick_positions = []

    # Assume data is 2D and we compute intervals for each feature
    for feature_index in range(data.shape[1]):  # Loop through each feature
        feature_data = data[:, feature_index]  # Extract data for the current feature
        for i in range(6):
            mask = (labels == i) & (confidence_scores[:, i] >= 0.73)
            filtered_data = feature_data[mask]
            
            if filtered_data.size > 0:
                interval = compute_confidence_intervals(filtered_data)
                data_list.append(filtered_data.tolist())
                intervals.append(interval)
                plotted_labels.append(f"{class_labels[i]} Feature {feature_index+1}")
                positions.append(base_position)
                color_assignment.append(colors[i])
                tick_positions.append(base_position)
                base_position += 1

    # Add your non-classifiable data handling here as needed

    return plot_results(data_list, intervals, plotted_labels, positions, color_assignment, tick_positions, plotted_labels)

def plot_results(data, intervals, labels, positions, color_assignment, tick_positions, plotted_labels):
    """Plots the results of the analysis."""
    plt.figure(figsize=(12, 8))
    for pos, (mean, lower, upper), color in zip(positions, intervals, color_assignment):
        plt.errorbar(pos, mean, yerr=[[mean - lower], [upper - mean]], fmt='o', color=color, label=labels[pos-1])

    plt.xticks(tick_positions, plotted_labels)
    plt.axhline(y=0.73, color='r', linestyle='--')
    plt.title('Classifier Predictions with Probability Thresholds and Confidence Intervals')
    plt.ylabel('Probability')
    plt.ylim(0, 1)
    plt.grid(True)
    plt.legend()
    plt.show()

    # Optionally save the plot to a file that can be displayed in a web app
    plt_path = 'static/temp_plot.png'  # Adjust as needed for your app
    plt.savefig(plt_path)
    plt.close()
    return plt_path

def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    
def generate_plots_task(H, labels, predictions):
     # Plotting directly within the function without needing to save to disk first
     confidence_plot = generate_confidence_plot(H, labels, predictions)
     logging.info("Plots generated successfully.")
     return confidence_plot
