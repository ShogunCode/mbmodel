import os
from joblib import load
import logging
from flask import Blueprint
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.svm import SVC

bp = Blueprint('model', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to make predictions using the SVM model
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
        confidence_scores = None

    logging.info("Predictions completed successfully.")

    return predictions, confidence_scores, H

# Test & Train Logic for Model
# Parameter grid for GridSearch
def test_train_svm(H, cluster_labels):
    
    # Assuming X is your feature matrix and y is your labels vector
    X_train_svm, X_test_svm, y_train_svm, y_test_svm = train_test_split(H, cluster_labels, test_size=0.2, random_state=42)

    # Configure the SVM model
    svm_model = SVC(kernel='linear')  # Starting point, linear kernel

    # Fit the model
    svm_model.fit(X_train_svm, y_train_svm)

    # Predict on the test set
    predictions_svm = svm_model.predict(X_test_svm)
    
    param_grid = {
        'C': [0.1, 1, 10, 100],  # C values
        'gamma': [1, 0.1, 0.01, 0.001],  # gamma values
        'kernel': ['rbf', 'poly', 'sigmoid']  # kernels
    }

# Grid Search for SVM
def grid_search_svm(X_train_svm, y_train_svm, X_test_svm):
    
    # Parameter grid for GridSearch
    param_grid = {
    'C': [0.1, 1, 10, 100],  # C values
    'gamma': [1, 0.1, 0.01, 0.001],  # gamma values
    'kernel': ['rbf', 'poly', 'sigmoid']  # kernels
}
    
    # Create a GridSearchCV object
    grid_search = GridSearchCV(SVC(), param_grid, refit=True, verbose=2, cv=10)

    # Fit it to the data
    grid_search.fit(X_train_svm, y_train_svm)

    # Print out the best parameters
    print("Best parameters found: ", grid_search.best_params_)

    # Predict using the best model
    predictions = grid_search.predict(X_test_svm)
