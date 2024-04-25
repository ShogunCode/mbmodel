import os
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
import pandas as pd
from flask import current_app
import logging
from app.module_model.model import make_predictions
import numpy as np

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
    

    






