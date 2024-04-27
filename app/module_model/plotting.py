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

def normalize_decision_function(confidence_scores):
    min_val = np.min(confidence_scores)
    max_val = np.max(confidence_scores)
    return 100 * (confidence_scores - min_val) / (max_val - min_val)

def analyze_data(confidence_scores_str, threshold=0.73):
    try:
        # Convert the input string to a numpy array
        confidence_scores = np.array(eval(confidence_scores_str))
        
        # Check if the array has the right shape
        if confidence_scores.ndim != 2 or confidence_scores.shape[1] != 7:
            raise ValueError("Input must be a 2D array with 7 columns representing clusters.")
    except SyntaxError as e:
        raise ValueError("Invalid input format: Please ensure the input string is a valid 2D list.") from e

    # Initialize an empty list to collect confidence scores for each cluster
    cluster_confidences = [[] for _ in range(confidence_scores.shape[1])]

    # Iterate through each sample and assign it to the correct cluster
    for sample in confidence_scores:
        # Find the index (cluster number) of the max confidence score if above threshold
        if max(sample) >= threshold:
            cluster_number = np.argmax(sample)
            cluster_confidences[cluster_number].append(max(sample))
        else:
            # If no confidence score exceeds the threshold, assign it to a 'no cluster'
            cluster_confidences.append([0])

    # Create the box plot
    plt.figure(figsize=(14, 8))
    bp = plt.boxplot(cluster_confidences, patch_artist=True, notch=True, vert=True, showfliers=True, widths=0.6)
    
    # Coloring each box
    colors = ['tan', 'lightblue', 'lightgreen', 'lavender', 'orange', 'lightpink', 'lightgray']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    # Adding titles and labels
    plt.title('Confidence Scores by Cluster')
    plt.xlabel('Cluster Number')
    plt.ylabel('Confidence Scores')
    plt.xticks(range(1, len(cluster_confidences) + 1), [f'Cluster {i+1}' for i in range(len(cluster_confidences))])
    plt.grid(True)
    
    # Save and show the plot
    plt_path = 'app/static/results/cluster_confidence_boxplot.png'
    plt.savefig(plt_path)
    # plt.show()
    
    return plt_path

# def analyze_data(data, labels, confidence_scores):
#     class_labels = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'NC']
#     colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'grey']
    
#     data_list, intervals, plotted_labels, positions, color_assignment = [], [], [], [], []
#     base_position = 1
#     tick_positions = []

#     for feature_index in range(data.shape[1]):
#         feature_data = data[:, feature_index]
#         for i in range(6):
#             mask = (labels == i) & (confidence_scores[:, i] >= 0.73)
#             filtered_data = feature_data[mask]
#             if filtered_data.size > 0:
#                 try:
#                     interval = compute_confidence_intervals(filtered_data)
#                     data_list.append(filtered_data.tolist())
#                     intervals.append(interval)
#                     plotted_labels.append(f"{class_labels[i]} Feature {feature_index+1}")
#                     positions.append(base_position)
#                     color_assignment.append(colors[i])
#                     tick_positions.append(base_position)
#                     base_position += 1
#                 except ValueError as e:
#                     print(f"Error computing intervals for {class_labels[i]} Feature {feature_index+1}: {e}")

#     # Further handle non-classifiable data here

#     return plot_results(data_list, intervals, plotted_labels, positions, color_assignment, tick_positions, plotted_labels)

# def plot_results(data, intervals, labels, positions, color_assignment, tick_positions, plotted_labels):
#     """Plots the results of the analysis."""
#     plt.figure(figsize=(12, 8))
#     for pos, (mean, lower, upper), color in zip(positions, intervals, color_assignment):
#         plt.errorbar(pos, mean, yerr=[[mean - lower], [upper - mean]], fmt='o', color=color, label=labels[pos-1])

#     plt.xticks(tick_positions, plotted_labels)
#     plt.axhline(y=0.73, color='r', linestyle='--')
#     plt.title('Classifier Predictions with Probability Thresholds and Confidence Intervals')
#     plt.ylabel('Probability')
#     plt.ylim(0, 1)
#     plt.grid(True)
#     plt.legend()
#     plt.show()

#     # Optionally save the plot to a file that can be displayed in a web app
#     plt_path = 'static/temp_plot.png'  # Adjust as needed for your app
#     plt.savefig(plt_path)
#     plt.close()
#     return plt_path

def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    
def generate_plots_task(H, labels, predictions):
     # Plotting directly within the function without needing to save to disk first
     confidence_plot = generate_confidence_plot(H, labels, predictions)
     logging.info("Plots generated successfully.")
     return confidence_plot
