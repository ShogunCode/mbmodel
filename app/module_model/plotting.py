import matplotlib.pyplot as plt
from matplotlib import cm
import seaborn as sns
import numpy as np
import io
import pandas as pd
import base64
from .model import make_predictions
import logging
import json

# Configure logging to show messages of severity INFO and above
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_data(confidence_scores, predictions, threshold):
    cluster_data = {}
    cluster_data['NC'] = []

    for idx, (score, prediction) in enumerate(zip(confidence_scores, predictions)):
        logging.info(f"Processing sample {idx}: score={score}, prediction={prediction}")

        # Convert prediction to an appropriate cluster label and adjust for zero-based index
        if prediction == 0:
            # Handle 'No Cluster' condition explicitly if 0 is used for this purpose
            cluster_label = 'NC'
        else:
            cluster_label = f'C{prediction}'

        # Ensure the cluster label exists in the dictionary
        if cluster_label not in cluster_data:
            cluster_data[cluster_label] = []

        try:
            # Append the score to the appropriate cluster
            # Since 'score' is already extracted and is a scalar, we use it directly
            cluster_data[cluster_label].append(score[0])  # Assuming score is a single-element array

        except Exception as e:
            logging.error(f"Error processing sample {idx} with prediction {prediction}: {e}")
            continue  # Optionally skip failing sample

    return cluster_data
def plot_cluster_data(cluster_data, threshold):
    fig, ax = plt.subplots(figsize=(12, 6))
    data_to_plot = [data for label, data in cluster_data.items()]
    labels = [label for label, data in cluster_data.items()]
    box = ax.boxplot(data_to_plot, patch_artist=True, vert=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(data_to_plot)))
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    plt.xticks(range(1, len(cluster_data) + 1), labels)
    plt.ylabel('Confidence Score')
    plt.title('Confidence Scores per Cluster')
    ax.legend()

    # Convert plot to PNG image in bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    
    # Encode PNG image to base64 string
    image_base64 = base64.b64encode(image_png)
    return image_base64.decode('utf-8')

def analyze_data(request_data):
    logging.info("Starting analysis of data")
    try:
        data = json.loads(request_data)

        if 'results' not in data:
            return {'error': "Missing 'results' key in the provided data."}

        confidence_scores = [item['confidence'] for item in data['results']]
        predictions = [item['cluster'] for item in data['results']]
        threshold = data.get('threshold', 0.73)

        # Checking the dimensionality of confidence_scores
        confidence_scores = np.array(confidence_scores)
        if confidence_scores.ndim == 1:
            # If it's a 1D array, we may need to reshape it to 2D if expected by other parts of your code
            # Assuming each score is independent and there's no clustering logic that splits them into features per sample
            confidence_scores = confidence_scores.reshape(-1, 1)  # Reshape to 2D if needed

        cluster_data = process_data(confidence_scores, predictions, threshold)
        plot_base64 = plot_cluster_data(cluster_data, threshold)

        return {'image': plot_base64}
    except Exception as e:
        logging.error("Error in analyze_data", exc_info=True)
        return {'error': str(e)}
    
# Function to encode the plot image for web display
def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    