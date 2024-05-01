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
import scipy.stats as stats
from flask import jsonify
import os

# Configure logging to show messages of severity INFO and above
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cluster_count(predictions):
    # Use numpy's unique function to find unique elements and their counts
    clusters, counts = np.unique(predictions, return_counts=True)
    # Convert clusters and counts to Python native int
    clusters = clusters.astype(int).tolist()  # Converts and makes a list of Python integers
    counts = counts.astype(int).tolist()  # Converts and makes a list of Python integers
    # Create a dictionary from clusters and counts
    cluster_counts = dict((cluster + 1, count) for cluster, count in zip(clusters, counts))
    return cluster_counts  # Return the dictionary directly

def process_csv(csv_path, output_dir):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_path)
    
    # Create a new DataFrame to hold processed data
    processed_data = pd.DataFrame()
    processed_data['Sample'] = df['Sample']
    processed_data['Predicted Cluster'] = df['Predicted Cluster']
    
    # Calculate the highest confidence score for each sample
    confidence_scores = df.iloc[:, 1:8]  # Assuming the first 7 columns after 'Sample' are confidence scores
    processed_data['Highest Probability Score'] = confidence_scores.max(axis=1)
    
    # Check if the output directory exists, if not, create it
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Define the path for the processed file
    basename = os.path.basename(csv_path)
    processed_filename = f'processed_{basename}'
    full_path = os.path.join(output_dir, processed_filename)
    
    # Save the processed data to CSV in the specified directory
    processed_data.to_csv(full_path, index=False)
    return full_path

def analyze_data(csv_file, threshold):
    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Extract cluster data 
    cluster_columns = [col for col in df.columns if col.startswith("Confidence Score Cluster")]
    data = df[cluster_columns]

    # Calculate the confidence intervals (assuming 95% confidence) and append them
    confidence_intervals = {}
    for col in cluster_columns:
        confidence_level = 0.95  # For a 95% confidence interval
        ci = stats.t.interval(confidence_level, df=len(data) - 1, loc=data[col].mean(), scale=stats.sem(data[col]))
        confidence_intervals[col] = ci

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    data_to_plot = [data[col].dropna().values for col in cluster_columns]  # Handle NaN values
    labels = cluster_columns
    box = ax.boxplot(data_to_plot, patch_artist=True, vert=True)
    colors = plt.cm.viridis(np.linspace(0, 1, len(data_to_plot)))
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    plt.xticks(range(1, len(labels) + 1), labels, rotation=45)  # Rotate labels if needed
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
    image_base64 = base64.b64encode(image_png).decode('utf-8')

    return image_base64

# def analyze_data(csv_file):
    # Read the CSV file
    # df = pd.read_csv(csv_file)

    # # Extract cluster data 
    # cluster_columns = [col for col in df.columns if col.startswith("Confidence Score Cluster")]
    # data = df[cluster_columns]

    # # Calculate the confidence intervals (assuming 95% confidence) and append them
    # confidence_intervals = {}
    # for col in cluster_columns:
    #     confidence_level = 0.95  # For a 95% confidence interval
    #     ci = stats.t.interval(confidence_level, df=len(data) - 1, loc=data[col].mean(), scale=stats.sem(data[col]))
    #     confidence_intervals[col] = ci

    # fig, ax = plt.subplots(figsize=(12, 6))
    
    # # Assuming `cluster_data` is a DataFrame where each column is a cluster
    # data_to_plot = [data[col].dropna().values for col in data.columns]
    # labels = data.columns.tolist()

    # # Create a boxplot
    # box = ax.boxplot(data_to_plot, patch_artist=True, vert=True)

    # # Color each box in the boxplot
    # colors = plt.cm.viridis(np.linspace(0, 1, len(data_to_plot)))
    # for patch, color in zip(box['boxes'], colors):
    #     patch.set_facecolor(color)

    # # Set x-ticks labels
    # plt.xticks(range(1, len(labels) + 1), labels)
    # plt.ylabel('Confidence Score')
    # plt.title('Confidence Scores per Cluster')
    # plt.show()

    # # Convert plot to PNG image in bytes
    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # plt.close(fig)
    # buf.seek(0)
    # image_png = buf.getvalue()
    # buf.close()

    # # Encode PNG image to base64 string and return
    # image_base64 = base64.b64encode(image_png).decode('utf-8')
    # return image_base64


# Not sending to Client-side, but sending a 202 Success :( 
# def analyze_data(csv_file):
    # Read the CSV file
    # df = pd.read_csv(csv_file)

    # # Extract cluster data 
    # cluster_columns = [col for col in df.columns if col.startswith("Confidence Score Cluster")]
    # data = df[cluster_columns] 

    # # Calculate the confidence intervals (assuming 95% confidence)
    # confidence_intervals = []
    # for col in cluster_columns:
    #     confidence_level = 0.95  # For a 95% confidence interval
    # ci = stats.t.interval(confidence_level, df=len(data) - 1, loc=df[col].mean(), scale=stats.sem(df[col]))

    # # Create the boxplot with Seaborn
    # sns.boxplot(data=data)

    # # Add confidence intervals lines 
    # plt.ylim(0, 1)  # Adjust the Y-axis limits for confidence scores
    # for i, ci in enumerate(confidence_intervals):
    #     y = ci[1]  # Upper bound of the confidence interval
    #     plt.plot([i+0.8, i+1.2], [y, y], linewidth=2, color='black')
    #     plt.scatter(i + 1, y, marker='o', color='white', s=30) 

    # # Labels and styling
    # plt.xticks(range(1, len(cluster_columns) + 1), cluster_columns)
    # plt.xlabel('Clusters')
    # plt.ylabel('Confidence Score')
    # plt.title('Confidence Interval Box Plot')
    # plt.grid(axis='y')
    
    # #Convert plot to PNG image in bytes
    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # plt.close()

    # buf.seek(0)
    # image_png = buf.getvalue()
    # buf.close()
    
    # # Encode PNG image to base64 string
    # image_base64 = base64.b64encode(image_png)
    # return image_base64.decode('utf-8')
    
# Functions working but wrong boxplot 
# def process_data(confidence_scores, predictions, threshold):
#     cluster_data = {}
#     cluster_data['NC'] = []

#     for idx, (score, prediction) in enumerate(zip(confidence_scores, predictions)):
#         logging.info(f"Processing sample {idx}: score={score}, prediction={prediction}")

#         # Convert prediction to an appropriate cluster label and adjust for zero-based index
#         if prediction == 0:
#             # Handle 'No Cluster' condition explicitly if 0 is used for this purpose
#             cluster_label = 'NC'
#         else:
#             cluster_label = f'C{prediction}'

#         # Ensure the cluster label exists in the dictionary
#         if cluster_label not in cluster_data:
#             cluster_data[cluster_label] = []

#         try:
#             # Append the score to the appropriate cluster
#             # Since 'score' is already extracted and is a scalar, we use it directly
#             cluster_data[cluster_label].append(score[0])  # Assuming score is a single-element array

#         except Exception as e:
#             logging.error(f"Error processing sample {idx} with prediction {prediction}: {e}")
#             continue  # Optionally skip failing sample

#     return cluster_data

# def plot_cluster_data(cluster_data, threshold):
    # fig, ax = plt.subplots(figsize=(12, 6))
    # data_to_plot = [data for label, data in cluster_data.items()]
    # labels = [label for label, data in cluster_data.items()]
    # box = ax.boxplot(data_to_plot, patch_artist=True, vert=True)
    # colors = plt.cm.viridis(np.linspace(0, 1, len(data_to_plot)))
    # for patch, color in zip(box['boxes'], colors):
    #     patch.set_facecolor(color)
    # plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    # plt.xticks(range(1, len(cluster_data) + 1), labels)
    # plt.ylabel('Confidence Score')
    # plt.title('Confidence Scores per Cluster')
    # ax.legend()

    # # Convert plot to PNG image in bytes
    # buf = io.BytesIO()
    # plt.savefig(buf, format='png')
    # plt.close(fig)
    # buf.seek(0)
    # image_png = buf.getvalue()
    # buf.close()
    
    # # Encode PNG image to base64 string
    # image_base64 = base64.b64encode(image_png)
    # return image_base64.decode('utf-8')

# def analyze_data(request_data):
#     logging.info("Starting analysis of data")
#     try:
#         data = json.loads(request_data)

#         if 'results' not in data:
#             return {'error': "Missing 'results' key in the provided data."}

#         confidence_scores = [item['confidence'] for item in data['results']]
#         predictions = [item['cluster'] for item in data['results']]
#         threshold = data.get('threshold', 0.73)

#         # Checking the dimensionality of confidence_scores
#         confidence_scores = np.array(confidence_scores)
#         if confidence_scores.ndim == 1:
#             # If it's a 1D array, we may need to reshape it to 2D if expected by other parts of your code
#             # Assuming each score is independent and there's no clustering logic that splits them into features per sample
#             confidence_scores = confidence_scores.reshape(-1, 1)  # Reshape to 2D if needed

#         cluster_data = process_data(confidence_scores, predictions, threshold)
#         plot_base64 = plot_cluster_data(cluster_data, threshold)

#         return {'image': plot_base64}
#     except Exception as e:
#         logging.error("Error in analyze_data", exc_info=True)
#         return {'error': str(e)}
    
# Function to encode the plot image for web display
def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    