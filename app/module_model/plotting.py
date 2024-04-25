import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import numpy as np
from io import BytesIO
import base64
from .model import make_predictions
import logging

def handle_confidence_plot(confidence_scores, H, cluster_labels):
    # Generate plots
    plot_path = generate_confidence_plot(H, cluster_labels, confidence_scores)  # Implement generate_plots
    # Encode plot for web display
    encoded_plot = encode_plot_for_web(plot_path)  # Implement encode_plot_for_web
    return encoded_plot

def generate_confidence_plot(H, cluster_labels, confidence_scores):
    plt.figure(figsize=(10, 6))
    plt.scatter(H[:, 0], H[:, 1], c=cluster_labels, cmap='viridis', marker='o', label='Cluster Labels')
    plt.colorbar()
    plt.title("Prediction Clusters")
    plt.xlabel("Feature 1")
    plt.ylabel("Feature 2")
    plt.legend()
    plt.grid(True)
    plt_path = 'temp_plot.png'
    plt.savefig(plt_path)
    plt.close()
    return plt_path

def generate_plots(W, H, labels, predictions):
    sns.set_theme(style="whitegrid")

    # Plotting the NMF Components
    plt.figure(figsize=(12, 6))
    for i, comp in enumerate(H):
        plt.subplot(1, len(H), i + 1)
        plt.bar(range(len(comp)), comp)
        plt.title(f'Component {i+1}')
    plt.tight_layout()
    nmf_components_plot = save_plot_to_string()

    # Plotting the Cluster Assignments
    plt.figure(figsize=(12, 6))
    scatter = plt.scatter(W[:, 0], W[:, 1], c=labels, cmap='viridis')
    plt.colorbar(scatter)
    plt.title('Cluster Assignments')
    plt.xlabel('Component 1 Scores')
    plt.ylabel('Component 2 Scores')
    clusters_plot = save_plot_to_string()

    # Return encoded plots as base64 strings for easy HTML embedding
    return nmf_components_plot, clusters_plot

def save_plot_to_string():
    """Save the current matplotlib plot to a base64 string."""
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.read()).decode('ascii')
    return image_base64

def cluster_sample_count(cluster_labels):
    sample_counts = np.bincount(cluster_labels)

    # Create a bar chart
    plt.figure(figsize=(10, 6))
    clusters = np.arange(1, len(sample_counts) + 1)
    plt.bar(clusters, sample_counts, color='skyblue')

    # Add labels and title
    plt.xlabel('Cluster Number')
    plt.ylabel('Number of Samples')
    plt.title('Number of Samples in Each Cluster')
    plt.xticks(clusters)

    # Save the plot to a BytesIO buffer instead of showing it directly
    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close()  # Close the plot to free up memory
    buf.seek(0)  # Go to the beginning of the BytesIO buffer

    # Encode the image in base64 to embed in HTML
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()  # Close the buffer to clean up

    return image_base64

def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    
def generate_plots_task(model_path, H, cluster_labels):
    try:
        logging.info("Starting prediction and plotting task...")
        predictions, confidence_scores, H, y = make_predictions(H, cluster_labels, model_path)
        logging.info("Predictions made, generating plots...")

        nmf_components_plot, clusters_plot = generate_plots(H, H, cluster_labels, predictions)

        if confidence_scores is not None:
            confidence_plot = handle_confidence_plot(confidence_scores, H, cluster_labels)
        else:
            confidence_plot = "Confidence scores not available"

        logging.info("Plots generated successfully.")
        return {
            'nmf_components_plot': nmf_components_plot,
            'clusters_plot': clusters_plot,
            'confidence_plot': confidence_plot,
            'status': 'success'
        }
    except Exception as e:
        logging.error("Error in generate_plots_task: {}".format(e), exc_info=True)
        return {
            'error': str(e),
            'status': 'error'
        }
