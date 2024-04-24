import os
from werkzeug.utils import secure_filename
from module_user import preprocess_data, process_file
from flask import Blueprint, jsonify, flash, redirect, request, url_for, render_template, current_app
from celery import Celery
from module_model.plotting import cluster_sample_count

bp = Blueprint('user', __name__)
celery_app = Celery('tasks', broker='redis://localhost:127.0.0.1:5000/')

@celery_app.task
def process_file_async(file_path):
    try:
        preprocess_data(file_path)
    except Exception as e:
        print(f"An error occurred during file processing: {e}")

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Make sure the file has a valid filename
    filename = secure_filename(file.filename)
    if filename == '':
        return jsonify({'error': 'Invalid file name'}), 400
    
    # Get the upload directory from the Flask app config
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        return jsonify({'message': 'File uploaded successfully', 'file_path': file_path}), 200
    except Exception as e:
        current_app.logger.error(f'Failed to save file: {str(e)}')
        return jsonify({'error': str(e)}), 500

@bp.route('/process', methods=['POST'])
def process_uploaded_file():
    file_path = request.json.get('file_path')
    if not file_path:
        return jsonify({'error': 'No file path provided'}), 400

    try:
        result = process_file(file_path)
        if result:
            return jsonify({'message': 'File processed successfully', 'data': result}), 200
        else:
            return jsonify({'error': 'Data is not suitable for processing'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
def handle_file_and_plot(file_path):
    results = process_file(file_path)
    if results:
        cluster_labels = results['labels']
        cluster_sample_count(cluster_labels)
    else:
        print("Failed to process file or no data to plot.")
    
@bp.route('/plot', methods=['POST'])
def upload_and_process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    
    try:
        handle_file_and_plot(file_path)  # Call the function after file is saved
        return jsonify({'message': 'File processed and plotted successfully'}), 200
    except Exception as e:
        current_app.logger.error(f'Failed to process file: {str(e)}')
        return jsonify({'error': str(e)}), 500