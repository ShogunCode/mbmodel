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

# Read a data file from the given file path and return a pandas DataFrame
def read_data_file(file_path):
    # Reads a data file from the given file path and returns a pandas DataFrame.
    try:
        # Split the directory and the filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        # Determine the delimiter based on the file extension
        delimiter = '\t' if filename.endswith('.txt') else ','
        # Read the file into a DataFrame
        df = pd.read_csv(file_path, sep=delimiter)
        # Check if the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"The file {file_path} does not exist.")
        
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

# Dimenionality Reduction of the data using NMF
def transform_with_nmf(df, n_components):
    if df is not None:
        print("Data shape before NMF:", df.shape)  # Log the shape of the data
        if df.shape[1] == 0:  # Check if there are no columns
            print("No data available for NMF.")
            return None, None
        model = NMF(n_components=n_components)
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
    kmeans = KMeans(n_clusters=n_clusters)
    kmeans.fit(H)
    return kmeans.labels_, kmeans

# Make predictions using the provided model
def process_file(file_path):
    logging.debug(f"Starting to process file: {file_path}")
    with current_app.app_context():
        logging.debug(f"Starting to process file: {file_path}")
        try:
            raw_data = read_data_file(file_path)
            df = preprocess_data(raw_data)
            if df is None or df.shape[1] <= 0:
                logging.warning("DataFrame is empty after preprocessing")
                return None
            
            logging.info("Applying NMF transformation")
            W, H = transform_with_nmf(df, current_app.config['N_METAGENES'])
            
            H = H.T
            
            logging.info("Applying K-means clustering")
            cluster_labels, kmeans = apply_kmeans(H, current_app.config['N_CLUSTERS'])
            
            logging.info("Making predictions")
            predictions = make_predictions(H, cluster_labels, current_app.config['ML_MODEL_PATH'])
            
            return {
                'W': W.tolist(), 
                'H': H.tolist(), 
                'labels': cluster_labels.tolist(),
                'predictions': [np.array(pred).tolist() for pred in predictions]
            }
        except Exception as e:
            logging.error(f"Failed during processing: {str(e)}")
            return None

# Format the results into a structured dictionary or object    
def format_result(W, H, labels, predictions):
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

def generate_json_response(confidences):
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



# Working version of generate_json_response  
# def generate_json_response(predictions, confidences, threshold):
#     results = []
#     try:
#         for idx, (pred, conf) in enumerate(zip(predictions, confidences)):
#             # If confidences are multidimensional, choose a specific score.
#             # Example: Using the maximum score from each set of confidence scores
#             if isinstance(conf, np.ndarray):
#                 conf = conf.max()  # or np.mean(conf), or any other appropriate measure

#             # Ensure the data types are serializable
#             result = {
#                 "sample": int(idx + 1),
#                 "cluster": int(pred),
#                 "confidence": float(f"{conf:.2f}")  # Format and convert to float
#             }
#             results.append(result)
        
#         # Append the threshold to the response
#         response = {
#             "results": results,
#             "threshold": threshold
#         }
#         json_response = json.dumps(response)
#     except Exception as e:
#         logging.error(f"Failed to generate JSON response: {repr(e)}")
#         raise RuntimeError("Failed to generate valid JSON response") from e
#     return json_response    
    
r = redis.Redis(host='localhost', port=6379, db=0)
def store_in_redis(task_id, json_response):
    r.set(task_id, json_response)
    r.expire(task_id, 3600)

def write_json_to_file(task_id, json_response):
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

def create_csv(predictions, confidence_scores, filename='output.csv'):
    # Define the headers for the CSV file
    headers = ['Sample'] + [f'Confidence Score Cluster {i+1}' for i in range(7)] + ['Predicted Cluster']
    
    # Open a new CSV file
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(headers)
        
        # Write each row of data
        for index, (prediction, scores) in enumerate(zip(predictions, confidence_scores)):
            row = [f'Sample_{index + 1}'] + list(scores) + [prediction]
            writer.writerow(row)