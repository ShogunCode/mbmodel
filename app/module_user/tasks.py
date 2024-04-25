from app.celery_utils import celery_app
import app.config as config
from app.module_data_processing.data_processing import process_file
from flask import current_app
from app.module_model.plotting import cluster_sample_count
import traceback
from app.module_data_processing.data_processing import preprocess_data, transform_with_nmf, apply_kmeans, make_predictions, read_data_file, format_result
from app.module_model.model import make_predictions
from app.module_model.plotting import handle_confidence_plot
from app.module_model.plotting import generate_plots_task

@celery_app.task
def test_task():
    try:
        print("Test task executed.")
        return "Success"
    except Exception as e:
        print(f"Error executing task: {str(e)}")
        raise  # Re-raise the exception to ensure it gets logged in Celery logs as well.
     
# This worked - Unsure of previous code!      
@celery_app.task
def process_file_async(file_path):
    from app import create_app  # Import moved inside the function
    app = create_app()
    with app.app_context():
        from app.module_data_processing.data_processing import process_file  # Import moved inside the context
        print(f"Processing file asynchronously: {file_path}")
        try:
            process_file(file_path)
        except Exception as e:
            print("Exception occurred within the context block.")
            traceback.print_exc()  # Print detailed traceback to standard output
            current_app.logger.error("An error occurred during file processing.", exc_info=True)
            raise  # Re-raise the exception for Celery to handle
           
# @celery_app.task
# def process_file_task(file_path):
#     try:
#         raw_data = read_data_file(file_path)
#         preprocessed_data = preprocess_data(raw_data)
#         W, H = transform_with_nmf(preprocessed_data, config['N_METAGENES'])
#         labels, kmeans = apply_kmeans(H, config['N_CLUSTERS'])
#         predictions = make_predictions(H, labels, config['ML_MODEL_PATH'])
#         confidence_plot = handle_confidence_plot(H, predictions)
#         return format_result(W, H, labels, predictions)
#     except Exception as e:
#         # Handle exception, possibly retry the task
#         raise e

@celery_app.task
def async_generate_plots(model_path, H, cluster_labels):
    return generate_plots_task(model_path, H, cluster_labels)
           
@celery_app.task
def handle_file_and_plot(file_path):
    results = process_file(file_path)
    if results:
        cluster_labels = results['labels']
        cluster_sample_count(cluster_labels)
    else:
        current_app.logger.error("Failed to process file or no data to plot.")
