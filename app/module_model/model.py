import os
from joblib import load
import logging
from flask import Blueprint

bp = Blueprint('model', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Model more suited for logging due to backend operation & sys admin
def make_predictions(H, cluster_labels, model_path):
    logging.info("Current working directory: " + os.getcwd())
    full_path = os.path.join(os.getcwd(), model_path)
    if os.path.exists(full_path):
        logging.info("File found at: " + full_path)
    else:
        logging.error("File not found at: " + full_path)
        raise FileNotFoundError("Model file not found at specified path.")

    logging.info("Loading the data.")
    X = H
    y = cluster_labels  # Not used in prediction currently

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
    
        # Decision function values can be used as confidence scores in many SVM applications
    if hasattr(svm_model, "decision_function"):
        confidence_scores = svm_model.decision_function(H)
    elif hasattr(svm_model, "predict_proba"):
        # If model supports probability estimates, use the max probability as confidence score
        confidence_scores = svm_model.predict_proba(H).max(axis=1)
    else:
        # If no confidence information is available, return None
        confidence_scores = None

    logging.info("Predictions completed successfully.")

    return predictions, confidence_scores, H, y
