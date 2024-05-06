import matplotlib.pyplot as plt
import numpy as np
import io
import pandas as pd
import base64
import logging
import scipy.stats as stats
import os

# Configure logging to show messages of severity INFO and above
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to plot the distribution of confidence scores per cluster
def cluster_count(predictions):
    logging.info("Calculating cluster counts")
    # Use numpy's unique function to find unique elements and their counts
    clusters, counts = np.unique(predictions, return_counts=True)
    # Convert numpy types to Python native types for JSON serialization
    cluster_counts = {str(cluster): int(count) for cluster, count in zip(clusters, counts)}
    return cluster_counts  # Return the dictionary directly

# Function to plot the distribution of confidence scores per cluster
def process_csv(csv_path, output_dir):
    logging.info(f"Processing CSV file: {csv_path}")
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

# Function to plot the distribution of confidence scores per cluster
def analyze_data(csv_file):
    logging.basicConfig(level=logging.INFO)
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Log the columns in the DataFrame to debug
    logging.info(f"Columns available in DataFrame: {df.columns.tolist()}")
    
    # Extract data for cluster columns
    cluster_columns = [col for col in df.columns if 'Confidence Score Cluster' in col]
    logging.info(f"Identifying cluster data columns: {cluster_columns}")
    
    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    data_to_plot = [df[col].dropna() for col in cluster_columns]
    labels = cluster_columns
    box = ax.boxplot(data_to_plot, patch_artist=True, vert=True)
    
    # Assign colors and set labels to include the most frequent predicted cluster for each cluster column
    colors = plt.cm.viridis(np.linspace(0, 1, len(data_to_plot)))
    for patch, color in zip(box['boxes'], colors):
        patch.set_facecolor(color)
    
    # Create new labels that include the cluster name associated with each score cluster
    new_labels = []
    for col in cluster_columns:
        cluster_number = col.split()[-1]  # Extract the cluster number from the column name
        # Find the most frequent cluster name associated with this score cluster
        most_common_cluster = df[df[col] == df[col].max()]['Predicted Cluster'].mode()[0]
        new_labels.append(f"{most_common_cluster}")
    
    plt.xticks(range(1, len(labels) + 1), new_labels, rotation=45)
    plt.ylabel('Confidence Score')
    plt.title('Confidence Scores per Cluster with Predicted Cluster Annotation')
    
    # Correctly prepare handles and labels for the legend
    handles, labels = [], []
    for color, label in zip(colors, new_labels):
        handle = plt.Line2D([0], [0], color=color, lw=4)
        handles.append(handle)
        labels.append(label)
    ax.legend(handles, labels)
    
    # Convert plot to PNG image in bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    image_png = buf.getvalue()
    buf.close()
    
    # Encode PNG image to base64 string
    image_base64 = base64.b64encode(image_png).decode('utf-8')
    
    logging.info("Plotting complete")
    return image_base64

# Function to encode the plot image for web display
def encode_plot_for_web(plot_path):
    with open(plot_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('ascii')
    