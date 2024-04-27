from flask import render_template, jsonify, request, Response
import json
from app.module_user.file_utils import save_uploaded_file
from app.module_user import bp
from app.module_user.tasks import process_file_async, test_task, async_generate_plots
import time

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
    
@bp.route('/plot', methods=['POST'])
def plot_clusters():
    data = request.get_json()
    model_path = data.get('model_path')
    H = data.get('H')  # Assuming H and cluster_labels are passed correctly; often, these will need parsing or validation
    cluster_labels = data.get('cluster_labels')

    if not model_path or H is None or cluster_labels is None:
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # Dispatch the plotting job to Celery
        task = async_generate_plots.delay(model_path, H, cluster_labels)
        return jsonify({
            'message': 'Plot generation initiated',
            'task_id': task.id  # Return the Celery task ID to the client
        }), 202
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/results/<task_id>', methods=['GET'])
def get_results(task_id):
    task = async_generate_plots.AsyncResult(task_id)  # Get the state of the task
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Plot generation is still in progress...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result,
            'status': 'Plot generation completed.'
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
    
@bp.route('/status/<task_id>', methods=['GET'])
def get_status(task_id):
    task = process_file_async.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Task is still processing'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # Exception raised
        }
    return jsonify(response)

@bp.route('/results_stream/<task_id>')
def results_stream(task_id):
    def generate():
        task = process_file_async.AsyncResult(task_id)
        while task.state not in ['SUCCESS', 'FAILURE']:
            time.sleep(2)  # Delay between checks
            task = process_file_async.AsyncResult(task_id)  # Refresh task status
            yield f"data: {json.dumps({'status': task.state})}\n\n"
        yield f"data: {json.dumps({'status': task.state, 'result': task.get() if task.state == 'SUCCESS' else 'Task failed'})}\n\n"
    return Response(generate(), mimetype='text/event-stream')

# Test task
#
# Testing the logic of process_file
# @celery_app.task
# def process_file_async(file_path):
#     return "Test successful with file path: " + str(file_path)

@bp.route('/trigger_test_task')
def trigger_test_task():
    # This line sends the task to Celery and executes it asynchronously
    task_result = test_task.delay()
    return jsonify({'status': 'Task submitted!', 'task_id': task_result.id})
