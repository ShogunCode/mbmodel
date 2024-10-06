import os
from werkzeug.utils import secure_filename
from flask import request, current_app
import logging
from app.config import Config

# Function to check if the file is allowed
def allowed_file(filename, allowed_extensions):
    logging.info("Checking if file is allowed")
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Function to save the uploaded file
def save_uploaded_file():
    logging.info("Saving uploaded file")
    if 'file' not in request.files:
        return None, 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return None, 'No selected file', 400

    filename = secure_filename(file.filename)
    if filename == '':
        return None, 'Invalid file name', 400

    # Check if the file's extension is allowed
    if not filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS:
        current_app.logger.error(f"Unsupported file extension for file: {filename}")
        return None, 'Unsupported file extension', 400

    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    print(f"File path: {file_path}")

    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)
        return file_path, None, 200
    except Exception as e:
        current_app.logger.error(f'Failed to save file: {str(e)}')
        return None, str(e), 500

# Function to read data from a file
def read_data(filepath):
    logging.info(f"Reading data from file: {filepath}")
    with open(filepath, 'r') as file:
        return file.read()

