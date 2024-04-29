from app.celery_utils import celery_app
import app.config as config
from flask import current_app
import traceback
from app.module_data_processing.data_processing import preprocess_data, transform_with_nmf, apply_kmeans, make_predictions, read_data_file, generate_json_response, store_in_redis, write_json_to_file, format_confidence_output, create_csv
from app.module_model.model import make_predictions
from app.module_model.plotting import analyze_data, process_csv
import logging

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
    # Try the config in here?
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
            labels, kmeans = apply_kmeans(actual_data_for_plotting, n_clusters)
            predictions, confidence_scores, _, _ = make_predictions(actual_data_for_plotting, labels, model_path)
            logging.info(f"Confidence Scores Shape: {confidence_scores.shape}")
            print(f"Confidence Scores: {confidence_scores}")
            print(f"Predictions: {predictions}")
            create_csv(predictions, confidence_scores, filename=f'{task_id}.csv') 
            #str_confidence_scores = format_confidence_output(confidence_scores)
            #print(f"Confidence Scores After Formatting: {confidence_scores}")
            #logging.info("Generating JSON response.")
            #json_response = generate_json_response(confidence_scores)
            #logging.info("json_respone generated")
            #print(json_response)
            #store_in_redis(task_id=str(process_file_async.request.id), json_response=json_response)
            #write_json_to_file(json_response, f"static/results/{process_file_async.request.id}.json")
            process_csv(f'{task_id}.csv')
            processed_filename = process_csv(f'processed_{task_id}.csv')
            plot_path = analyze_data(f'{task_id}.csv', threshold=0.60)
            return {'processed_file': processed_filename, 'image': plot_path}
        except Exception as e:
            print("Exception occurred within the context block.")
            traceback.print_exc()  # Print detailed traceback to standard output
            current_app.logger.error("An error occurred during file processing.", exc_info=True)
            raise  # Re-raise the exception for Celery to handle
           