import os
from sklearn.decomposition import NMF
from sklearn.cluster import KMeans
import pandas as pd
from flask import current_app
import logging
from app.module_model.model import make_predictions


def process_file(file_path):
    logging.debug(f"Starting to process file: {file_path}")
    with current_app.app_context():
        logging.debug(f"Starting to process file: {file_path}")
        try:
            df = preprocess_data(file_path)
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
                'predictions': predictions.tolist()
            }
        except Exception as e:
            logging.error(f"Failed during processing: {str(e)}")
            return None
    
# Pre-process the data once it has been uploaded
def preprocess_data(file_path):
    try:
        # Split the directory and the filename
        directory = os.path.dirname(file_path)
        filename = os.path.basename(file_path)
        # Combine the directory path and filename into a full path
        full_file_path = os.path.join(directory, filename)
        # Determine the delimiter based on the file extension
        delimiter = '\t' if filename.endswith('.txt') else ','
        # Read the file into a DataFrame
        df = pd.read_csv(full_file_path, sep=delimiter)
        df = df.set_index('ID_REF')
        print("Dataframe loaded")
        print("DataFrame shape:", df.shape)
        print("DataFrame head:", df.head())
    except FileNotFoundError:
        print("File not found. Please check the file path and try again.")
    except pd.errors.EmptyDataError:
        print("No data: The file is empty.")
    except pd.errors.ParserError:
        print("Error parsing data. Check the file format and delimiter.")
    except Exception as e:
        print("An error occurred:", e)
        df = None
    # df = preprocess_data('uploads/ten_columns.txt')
    # print(df)

    if df is not None:
        print("DataFrame shape:", df.shape)
        print("DataFrame head:", df.head())
    else:
        print("Failed to process data. DataFrame is None.")

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

