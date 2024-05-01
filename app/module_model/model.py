import os
from joblib import load
import logging
from flask import Blueprint
import numpy as np

bp = Blueprint('model', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Model more suited for logging due to backend operation & sys admin
def make_predictions(H, model_path):
    logging.info("Current working directory: " + os.getcwd())
    full_path = os.path.join(os.getcwd(), model_path)
    if os.path.exists(full_path):
        logging.info("File found at: " + full_path)
    else:
        logging.error("File not found at: " + full_path)
        raise FileNotFoundError("Model file not found at specified path.")

    logging.info("Loading the data.")
    X = H

    try:
        logging.info(f"Loading the SVM model from {full_path}.")
        svm_model = load(full_path)
        logging.info(f"Model type after loading: {type(svm_model)}")
    except FileNotFoundError:
        logging.error(f"The model file {full_path} was not found.")
        raise
    except Exception as e:
        logging.error(f"An error occurred while loading the model: {str(e)}")
        raise

    try:
        logging.info("Making predictions.")
        predictions = svm_model.predict(X)
    except AttributeError as e:
        logging.error(f"An error occurred during prediction: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"An error occurred during prediction: {str(e)}")
        raise
    
    # Retrieve decision function or probability estimates
    if hasattr(svm_model, "decision_function"):
        confidence_scores = svm_model.decision_function(H)
        # Normalize confidence scores to [0, 1] for interpretation
        confidence_scores = (confidence_scores - confidence_scores.min()) / (confidence_scores.max() - confidence_scores.min())
        # Round confidence scores to 3 decimal places
        confidence_scores = np.around(confidence_scores, decimals=3)
    elif hasattr(svm_model, "predict_proba"):
        confidence_scores = svm_model.predict_proba(H)
        # Take the maximum probability as confidence
        confidence_scores = np.max(confidence_scores, axis=1)
        # Round confidence scores to 3 decimal places
        confidence_scores = np.around(confidence_scores, decimals=3)
    else:
        # If no confidence information is available, return None
        confidence_scores = Noneconfidence_scores = None

    logging.info("Predictions completed successfully.")

    return predictions, confidence_scores, H
