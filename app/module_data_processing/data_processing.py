import os
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
import pandas as pd
from flask import current_app
import logging
from app.module_model.model import make_predictions
import numpy as np
import json
import redis
import re
import csv
from app.config import Config 
from joblib import load

# Set up basic configuration for logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Read a data file from the given file path and return a pandas DataFrame
def read_data_file(file_path):
    try:
        # Split the directory and the filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        # Check if the file's extension is allowed
        if not filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS:
            logging.error(f"Unsupported file extension for file: {filename}")
            return None

        # Determine the delimiter based on the file extension
        delimiter = '\t' if filename.endswith('.txt') else ','

        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")

        # Read the file into a DataFrame
        df = pd.read_csv(file_path, sep=delimiter)
        return df

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
    except pd.errors.EmptyDataError:
        logging.error("No data: The file is empty.")
    except pd.errors.ParserError:
        logging.error("Error parsing data. Check the file format and delimiter.")
    except Exception as e:
        logging.error(f"An unexpected error occurred while reading the file: {e}")
    
    return None  # Return None if any error occurred

# Preprocess the data by setting the index and performing any necessary transformations
def preprocess_data(df):
    # Apply preprocessing steps to the raw DataFrame.
    # Check if the DataFrame is empty or not a DataFrame
    if df is None or not isinstance(df, pd.DataFrame):
        raise ValueError("Input is not a valid pandas DataFrame or it is None.")
    
    df = df.set_index('ID_REF')
    print("Dataframe loaded")
    print("DataFrame shape:", df.shape)
    print("DataFrame head:", df.head())

    return df

# Dimensionality Reduction of the data using NMF
def transform_with_nmf(df, n_components):
    logging.info("Starting NMF transformation")
    if df is not None:
        print("Data shape before NMF:", df.shape)  # Log the shape of the data
        if df.shape[1] == 0:  # Check if there are no columns
            print("No data available for NMF.")
            return None, None
        
        # Load the pre-trained NMF model from the specified path
        model = load(Config.NMF_MODEL_PATH)
        
        # Perform transformation using the pre-loaded model
        W = model.fit_transform(df) 
        H = model.components_
        
        # Debugging output for successful NMF transformation
        print("NMF transformation successful. Components shape:", H.shape)
        return W, H
    else:
        print("No data provided for NMF.")
        return None, None

# Apply KMeans clustering to the data
def apply_kmeans(H, n_clusters=7):
    logging.info("Applying K-means clustering")
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(H)
    return kmeans.labels_, kmeans

# Format the results into a structured dictionary or object    
def format_result(W, H, labels, predictions):
    logging.info("Formatting results")
    # Format the results into a structured dictionary or object
    return {
        'W': W.tolist(), 
        'H': H.tolist(), 
        'labels': labels.tolist(),
        'predictions': [np.array(pred).tolist() for pred in predictions]
    }
    
    
    
#def generate_json_response(predictions, confidences, threshold):
    results = []
    try:
        for idx, (pred, conf) in enumerate(zip(predictions, confidences)):
            # If confidences are multidimensional, choose a specific score.
            # Example: Using the maximum score from each set of confidence scores
            if isinstance(conf, np.ndarray):
                conf = conf.max()  # or np.mean(conf), or any other appropriate measure

            # Ensure the data types are serializable
            result = {
                "sample": int(idx + 1),
                "cluster": int(pred),
                "confidence": float(f"{conf:.2f}")  # Format and convert to float
            }
            results.append(result)
        
        # Append the threshold to the response
        response = {
            "results": results,
            "threshold": threshold
        }
        json_response = json.dumps(response)
    except Exception as e:
        logging.error(f"Failed to generate JSON response: {repr(e)}")
        raise RuntimeError("Failed to generate valid JSON response") from e
    return json_response

# Generate a JSON response from the confidence scores
def generate_json_response(confidences):
    logging.info("Generating JSON response")
    num_clusters = confidences.shape[1]  # Number of columns in the array
    response = []  # List to hold cluster-wise data
    
    for cluster_index in range(num_clusters):
        cluster_scores = confidences[:, cluster_index]  # Extract scores for the current cluster
        cluster_info = {
            "Cluster": cluster_index + 1,
            "Confidence Scores": cluster_scores.tolist()  # Convert array to list for JSON compatibility
        }
        response.append(cluster_info)
    
    # Convert the list to a JSON-formatted string
    return json.dumps(response)

r = redis.Redis(host='localhost', port=6379, db=0)
# Store the JSON response in Redis with a time-to-live (TTL) of 1 hour
def store_in_redis(task_id, json_response):
    r.set(task_id, json_response)
    r.expire(task_id, 3600)

# Retrieve the JSON response from Redis
def write_json_to_file(task_id, json_response):
    logging.info("Writing JSON response to file")
    # Sanitize task_id to ensure it's valid for file names
    sanitized_task_id = re.sub(r'[\\/*?:"<>|]', "", task_id)
    file_path = f"static/results/{sanitized_task_id}_result.json"
    
    print(f"Sanitized Task ID: {sanitized_task_id}")
    print(f"File Path: {file_path}")

    try:
        with open(file_path, "w") as file:
            # Ensure json_response is a string in JSON format
            if not isinstance(json_response, str):
                json_response = json.dumps(json_response)
            file.write(json_response)
    except Exception as e:
        print(f"Failed to write to file {file_path}: {e}")

# Cleans the output of confidence scores.
def format_confidence_output(confidence_scores):
    logging.info("Formatting confidence scores")
    # Convert the numpy array to a string format, ensuring commas and precise formatting
    array_string = np.array2string(confidence_scores, separator=', ', threshold=np.inf, max_line_width=np.inf, precision=3)
    
    # Adjust the string to ensure correct formatting:
    # Strip the array to its core representation by removing the outer brackets
    clean_string = array_string.strip('[]')
    
    # Split the string by rows of the original array
    rows = clean_string.split(']\n [')
    
    # Reformat each row to ensure proper formatting, maintaining brackets and spaces
    formatted_rows = ['[' + row.strip().replace('\n', '').replace(' ', '') + ']' for row in rows]
    
    # Join the rows with a newline character for clear separation
    formatted_string = ',\n'.join(formatted_rows)
    
    return '[' + formatted_string + ']'

# Create a CSV file with the predictions and confidence scores
def create_csv(predictions, confidence_scores, filename='output.csv'):
    logging.info("Starting to create CSV file")
    headers = ['Sample'] + [f'Confidence Score Cluster {i+1}' for i in range(7)] + ['Predicted Cluster']
    
    output_dir = Config.CSV_OUTPUT_DIR
    logging.debug(f"Output directory: {output_dir}")

    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created directory: {output_dir}")
    
        full_path = os.path.join(output_dir, filename)
        with open(full_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for index, (prediction, scores) in enumerate(zip(predictions, confidence_scores)):
                row = [f'Sample_{index + 1}'] + list(scores) + [prediction]
                writer.writerow(row)
            logging.info(f"CSV file created successfully at {full_path}")
    except Exception as e:
        logging.error("Failed to create CSV file", exc_info=True)
        raise  # Optionally re-raise the exception after logging it

    return full_path