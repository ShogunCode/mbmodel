from flask import render_template, jsonify, request
from app.module_user.file_utils import save_uploaded_file
from app.module_user import bp
from app.module_user.tasks import process_file_async, test_task, handle_file_and_plot

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
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400

    try:
        handle_file_and_plot(file_path)
        return jsonify({'message': 'File processed and plotted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
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