from app.celery_utils import celery_app
from app.module_data_processing.data_processing import process_file
from flask import current_app
from app.module_model.plotting import cluster_sample_count
import traceback


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
           
@celery_app.task
def handle_file_and_plot(file_path):
    results = process_file(file_path)
    if results:
        cluster_labels = results['labels']
        cluster_sample_count(cluster_labels)
    else:
        current_app.logger.error("Failed to process file or no data to plot.")
