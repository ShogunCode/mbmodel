from flask import Flask, request, flash, redirect, url_for
from first_start.config import Config
from first_start.utils import allowed_file, save_file, read_data
from first_start.data_processing import transform_with_nmf, apply_kmeans
from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
import joblib

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads/'

# Load SVM Model (if needed)
# model_svm = joblib.load('svm_model.joblib')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    
    if file and allowed_file(file.filename, app.config['ALLOWED_EXTENSIONS']):
        file_path = save_file(file, app.config['UPLOAD_FOLDER'])
        data = read_data(file_path)
        if data is not None:
            W, H = transform_with_nmf(data, app.config['N_METAGENES'])
            cluster_labels, kmeans = apply_kmeans(H, app.config['N_CLUSTERS'])
            flash('File successfully uploaded and processed.')
        else:
            flash('Invalid file format. Only CSV and TXT files are allowed.')
            return redirect(url_for('index'))
    else:
        flash('Invalid file format. Only CSV and TXT files are allowed.')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)