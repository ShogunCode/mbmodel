from app.celery_utils import celery_app
from app.config import Config
from flask import current_app
import traceback
from app.module_data_processing.data_processing import preprocess_data, transform_with_nmf, apply_kmeans, make_predictions, read_data_file, create_csv
from app.module_model.model import make_predictions
from app.module_model.plotting import analyze_data, process_csv, cluster_count
import logging

# Test task to ensure Celery is working correctly
@celery_app.task
def test_task():
    try:
        print("Test task executed.")
        return "Success"
    except Exception as e:
        print(f"Error executing task: {str(e)}")
        raise  # Re-raise the exception to ensure it gets logged in Celery logs as well.

# Task to process uploaded file - read, preprocess, transform, cluster, predict, plot
# /predict route calls this task
@celery_app.task
def process_file_async(file_path):
    # get the task ID
    task_id = process_file_async.request.id
    print(f"Task ID: {task_id}")
    from app import create_app 
    app = create_app()
    with app.app_context():
        try:
            logging.info(f"Processing file: {file_path}")
            logging.info(f"Task ID: {task_id}")
            logging.info("reading data file...")
            raw_data = read_data_file(file_path)
            logging.info("preprocessing data...")
            preprocessed_data = preprocess_data(raw_data)
            logging.info("transforming data with NMF...")
            W, H = transform_with_nmf(preprocessed_data, Config.N_METAGENES)
            print(f"H Shape: {H.shape}")
            actual_data_for_plotting = H.T  # The actual 2D data matrix for plotting
            # labels, kmeans = apply_kmeans(actual_data_for_plotting, n_clusters)
            logging.info("making predictions...")
            predictions, confidence_scores, _ = make_predictions(actual_data_for_plotting, Config.ML_MODEL_PATH)
            print(f"Confidence Scores: {confidence_scores}")
            print(f"Predictions: {predictions}")
            create_csv(predictions, confidence_scores, filename=f'{task_id}.csv') 
            json_cluster_count = cluster_count(predictions)
            processed_filename = process_csv(Config.CSV_OUTPUT_DIR + f'{task_id}.csv', Config.CSV_OUTPUT_DIR)
            plot_path = analyze_data(Config.CSV_OUTPUT_DIR + f'{task_id}.csv')
            return {'processed_file': processed_filename, 'image': plot_path, 'cluster_count': json_cluster_count}
        except Exception as e:
            print("Exception occurred within the context block.")
            traceback.print_exc()  # Print detailed traceback to standard output
            current_app.logger.error("An error occurred during file processing.", exc_info=True)
            raise  # Re-raise the exception for Celery to handle
           