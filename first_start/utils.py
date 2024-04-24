from flask import flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import pandas as pd

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return file_path

def read_data(file_path):
    if file_path.lower().endswith('.csv'):
        return pd.read_csv(file_path)
    elif file_path.lower().endswith('.txt'):
        return pd.read_csv(file_path, delimiter='\t')
    else:
        return None
