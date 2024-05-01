from flask import render_template, jsonify, request, Response, send_from_directory
import json
from app.module_user.file_utils import save_uploaded_file
from app.module_user import bp
from app.module_user.tasks import process_file_async, test_task
import time
import pandas as pd
import os
from app.config import Config

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    file_path, error_message, status_code = save_uploaded_file()
    if file_path:
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), status_code
    else:
        return jsonify({'error': error_message}), status_code

@bp.route('/process', methods=['POST'])
def process_uploaded_file():
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400
    try:
        result = process_file_async.delay(file_path)
        return jsonify({'message': 'File processing initiated', 'task_id': result.id}), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# Flask route to check the status of an ongoing task
@bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    # Retrieve the status of the task from Celery
    task = process_file_async.AsyncResult(task_id)

    # Create a response based on the task state
    if task.state == 'PENDING':
        response = {'state': task.state, 'status': 'Task is still processing'}
    elif task.state == 'SUCCESS':
        response = {'state': task.state, 'result': task.result}
    elif task.state == 'FAILURE':
        response = {'state': task.state, 'status': str(task.info)}  # Exception info
    else:
        response = {'state': task.state, 'status': 'Task is in an unknown state'}

    # Return the task status as a JSON response
    return jsonify(response)

@bp.route('/cluster-data/<task_id>', methods=['GET'])
def cluster_data(task_id):
    task = process_file_async.AsyncResult(task_id)
    if task.state == 'SUCCESS':
        result = task.get()
        
        return jsonify(result['cluster_count'])  # Use jsonify to return a JSON response
    elif task.state == 'FAILURE':
        return jsonify({'error': 'Failed to process file'}), 500
    else:
        return jsonify({'message': 'Data not ready'}), 202

@bp.route('/get-results/<csv_filename>')
def get_results(csv_filename):
    # Ensure the filename does not contain unsafe path elements
    if '..' in csv_filename or '/' in csv_filename:
        return jsonify({'error': 'Invalid path'}), 400

    # Build the full path to the CSV file
    csv_directory = Config.CSV_OUTPUT_DIR
    csv_path = os.path.join(csv_directory, csv_filename)

    try:
        # Check if the file exists and is a file, not a directory
        if not os.path.isfile(csv_path):
            return jsonify({'error': 'File not found'}), 404

        # Read the CSV file into a DataFrame
        data = pd.read_csv(csv_path)

        # Check if the DataFrame is empty
        if data.empty:
            return jsonify({'error': 'No data available'}), 200

        # Convert DataFrame to a dictionary in record orientation and send as JSON
        return jsonify(data.to_dict(orient='records'))
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500

# @bp.route('/get-results/<path:csv_filename>')
# def get_results(csv_filename):
#     # Use Flask's open_resource method to access files in the root directory
#     try:
#         csv_path = os.path.join(bp.root_path, csv_filename)
#         print(f"Looking for file at: {csv_path}")  # Diagnostic print
        
#         # Check if file exists
#         if not os.path.isfile(csv_path):
#             print("File not found.")  # Diagnostic print
#             return "File not found", 404  # Provide a 404 response
        
#         # File exists, proceed to read and return data
#         processed_data = pd.read_csv(csv_path)
#         return processed_data.to_json(orient='records')
#     except Exception as e:
#         print(f"An error occurred: {e}")  # Diagnostic print
#         return str(e), 500  # Return a 500 Internal Server Error with the exception

@bp.route('/trigger_test_task')
def trigger_test_task():
    # This line sends the task to Celery and executes it asynchronously
    task_result = test_task.delay()
    return jsonify({'status': 'Task submitted!', 'task_id': task_result.id})
