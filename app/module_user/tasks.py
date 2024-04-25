from app.celery_utils import celery_app
import app.config as config
from app.module_data_processing.data_processing import process_file
from flask import current_app
import traceback
from app.module_data_processing.data_processing import preprocess_data, transform_with_nmf, apply_kmeans, make_predictions, read_data_file, format_result
from app.module_model.model import make_predictions
from app.module_model.plotting import analyze_data, generate_plots_task

@celery_app.task
def test_task():
    try:
        print("Test task executed.")
        return "Success"
    except Exception as e:
        print(f"Error executing task: {str(e)}")
        raise  # Re-raise the exception to ensure it gets logged in Celery logs as well.
     
# This worked - Unsure of previous code!      
# @celery_app.task
# def process_file_async(file_path):
#         try:
#             process_file(file_path)
#         except Exception as e:
#             print("Exception occurred within the context block.")
#             traceback.print_exc()  # Print detailed traceback to standard output
#             current_app.logger.error("An error occurred during file processing.", exc_info=True)
#             raise  # Re-raise the exception for Celery to handle
           
# @celery_app.task
# def process_file_async(file_path):
#     from app import create_app  # Import moved inside the function
#     app = create_app()
#     with app.app_context():
#         from app.module_data_processing.data_processing import (
#             read_data_file, preprocess_data, transform_with_nmf, apply_kmeans, make_predictions, generate_plots_task
#         )
#     try:
#         n_metagenes = config['N_METAGENES']
#         n_clusters = config['N_CLUSTERS']
#         model_path = config['ML_MODEL_PATH']
#         raw_data = read_data_file(file_path)
#         preprocessed_data = preprocess_data(raw_data)
#         W, H = transform_with_nmf(preprocessed_data, n_metagenes)
#         labels, kmeans = apply_kmeans(H, n_clusters)
#         predictions = make_predictions(H, labels, model_path)
#         plots = generate_plots_task(model_path, H.T, labels)
#         return plots
#     except Exception as e:
#         print("Exception occurred within the context block.")
#         traceback.print_exc()  # Print detailed traceback to standard output
#         current_app.logger.error("An error occurred during file processing.", exc_info=True)
#         raise  # Re-raise the exception for Celery to handle

@celery_app.task
def process_file_async(file_path):
    from app import create_app  # Import moved inside the function
    app = create_app()
    with app.app_context():
        try:
            n_metagenes = 6
            n_clusters = 7
            model_path = 'app/module_model/svm_model.joblib'
            raw_data = read_data_file(file_path)
            preprocessed_data = preprocess_data(raw_data)
            W, H = transform_with_nmf(preprocessed_data, n_metagenes)
            
            actual_data_for_plotting = H.T  # The actual 2D data matrix for plotting
            labels, kmeans = apply_kmeans(actual_data_for_plotting, n_clusters=7)
            predictions, confidence_scores, _, _ = make_predictions(actual_data_for_plotting, labels, model_path)
            plot_path = analyze_data(actual_data_for_plotting, labels, confidence_scores)

            # labels, kmeans = apply_kmeans(H.T, n_clusters)
            # predictions = make_predictions(H.T, labels, model_path)
            # plots = generate_plots_task(predictions, H.T, labels)
            return plot_path
        except Exception as e:
            print("Exception occurred within the context block.")
            traceback.print_exc()  # Print detailed traceback to standard output
            current_app.logger.error("An error occurred during file processing.", exc_info=True)
            raise  # Re-raise the exception for Celery to handle

@celery_app.task
def async_generate_plots(model_path, H, cluster_labels):
    return generate_plots_task(model_path, H, cluster_labels)
           
# @celery_app.task
# def handle_file_and_plot(file_path):
#     results = process_file(file_path)
#     if results:
#         cluster_labels = results['labels']
#         cluster_sample_count(cluster_labels)
#     else:
#         current_app.logger.error("Failed to process file or no data to plot.")
