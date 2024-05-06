import os
import pytest
from werkzeug.datastructures import FileStorage
from flask import Flask, request
from io import BytesIO
from unittest.mock import MagicMock

from app.module_user.file_utils import allowed_file, save_uploaded_file, read_data

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = '/path/to/upload'
    return app

@pytest.fixture
def client(app):
    with app.test_client() as client:
        with app.app_context():
            yield client

def test_allowed_file():
    allowed_extensions = {'txt', 'pdf', 'png'}
    assert allowed_file('document.pdf', allowed_extensions)
    assert not allowed_file('document.exe', allowed_extensions)
    assert not allowed_file('document', allowed_extensions)

def test_save_uploaded_file(app, client, mocker):
    mocker.patch('os.makedirs')
    save_mock = mocker.patch('werkzeug.datastructures.FileStorage.save')

    # Simulate an endpoint for testing file uploads
    @app.route('/upload', methods=['POST'])
    def upload_route():
        file_storage = request.files.get('file')
        if file_storage:
            filename = file_storage.filename
            if filename != '':
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_storage.save(file_path)
                return "File uploaded", 200
            else:
                return "No file name provided", 400
        return "No file part", 400

    with app.test_request_context():
        client.application.config['UPLOAD_FOLDER'] = '/fake/directory'
        
        # Test uploading a correct file
        data = {'file': (BytesIO(b"file content"), 'test.txt')}
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 200
        save_mock.assert_called_once_with('/fake/directory/test.txt')

        # Test uploading with no file part
        response = client.post('/upload', content_type='multipart/form-data')
        assert response.status_code == 400

        # Test uploading an empty file name
        data['file'] = (BytesIO(b""), '')
        response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

def test_read_data(mocker):
    mock_open = mocker.patch('builtins.open', mocker.mock_open(read_data="test data"))
    data = read_data('/fake/path/test.txt')
    mock_open.assert_called_once_with('/fake/path/test.txt', 'r')
    assert data == 'test data'
