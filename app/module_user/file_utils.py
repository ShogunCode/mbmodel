import os
from werkzeug.utils import secure_filename
from flask import request, current_app

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file():
    if 'file' not in request.files:
        return None, 'No file part', 400

    file = request.files['file']
    if file.filename == '':
        return None, 'No selected file', 400

    filename = secure_filename(file.filename)
    if filename == '':
        return None, 'Invalid file name', 400

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

def read_data(filepath):
    with open(filepath, 'r') as file:
        return file.read()

