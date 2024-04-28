from flask import render_template, jsonify, request, Response
import json
from app.module_user.file_utils import save_uploaded_file
from app.module_user import bp
from app.module_user.tasks import process_file_async, test_task
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

@bp.route('/trigger_test_task')
def trigger_test_task():
    # This line sends the task to Celery and executes it asynchronously
    task_result = test_task.delay()
    return jsonify({'status': 'Task submitted!', 'task_id': task_result.id})
