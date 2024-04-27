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

def analyze_data(predictions, labels, confidence_scores, threshold=0.73):
    n_samples = predictions.shape[0]
    n_clusters = np.max(predictions) + 1  # Assuming predictions are 0-indexed cluster IDs
    class_labels = [f'Cluster {i+1}' for i in range(n_clusters)] + ['Non-classified']

    normalize_decision_function(confidence_scores)

    plt.figure(figsize=(14, 8))

    data_to_plot = [[] for _ in range(n_clusters + 1)]  # +1 for non-classified category

    for i in range(n_samples):
        cluster_index = predictions[i]
        max_confidence = np.max(confidence_scores[i])
        if max_confidence < threshold * 100:
            data_to_plot[-1].append(max_confidence)  # Non-classified category
        else:
            data_to_plot[cluster_index].append(max_confidence)

    positions = np.arange(1, n_clusters + 2)
    bp = plt.boxplot(data_to_plot, positions=positions, patch_artist=True, notch=True, vert=True, showfliers=True, widths=0.6)
    colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'grey', 'black']  # Additional color for non-classified

    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)

    plt.xticks(positions, class_labels)
    plt.axhline(y=threshold * 100, color='r', linestyle='--')
    plt.title('SVM Classifier Confidence by Predicted Cluster and Non-classified')
    plt.ylabel('Confidence Score (%)')
    plt.ylim(0, 100)
    plt.grid(True)
    #plt.show()

    # Save the plot to a file before showing it
    plt_path = 'app/static/results/classifier_confidence_results.png'
    plt.savefig(plt_path)
    #plt.close()  # Close the plot to free up memory


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
