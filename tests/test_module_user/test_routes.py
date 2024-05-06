import pytest
from flask import url_for
from io import BytesIO
from unittest.mock import patch
from app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "UPLOAD_FOLDER": '/tmp'
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_index(client):
    response = client.get(url_for('user.index'))
    assert response.status_code == 200
    assert 'text/html' in response.content_type

def test_upload_file(client):
    data = {'file': (BytesIO(b"test content"), 'test.txt')}
    response = client.post(url_for('user.upload_file'), data=data, content_type='multipart/form-data')
    assert response.status_code == 200
    assert 'File uploaded successfully' in response.get_json()['message']

def test_process_uploaded_file_no_filepath(client):
    response = client.post(url_for('user.process_uploaded_file'), json={'file_path': ''})
    assert response.status_code == 400
    assert 'No file path provided' in response.get_json()['error']

@patch('app.module_user.tasks.process_file_async.delay')
def test_process_uploaded_file(mock_delay, client):
    mock_delay.return_value.id = '123'
    response = client.post(url_for('user.process_uploaded_file'), json={'file_path': '/tmp/test.txt'})
    assert response.status_code == 202
    assert 'File processing initiated' in response.get_json()['message']

def test_get_status_pending(mock_delay, client):
    mock_delay.return_value.AsyncResult.return_value.state = 'PENDING'
    response = client.get(url_for('user.get_status', task_id='123'))
    assert response.status_code == 200
    assert 'Task is still processing' in response.get_json()['status']

def test_cluster_data_success(mock_delay, client):
    mock_delay.return_value.AsyncResult.return_value.state = 'SUCCESS'
    mock_delay.return_value.AsyncResult.return_value.get.return_value = {'cluster_count': 5}
    response = client.get(url_for('user.cluster_data', task_id='123'))
    assert response.status_code == 200
    assert response.get_json() == 5

def test_get_results_file_not_found(client):
    response = client.get(url_for('user.get_results', csv_filename='invalid.csv'))
    assert response.status_code == 404
    assert 'File not found' in response.get_json()['error']

@pytest.mark.parametrize("csv_filename", ["../path/to/file.csv", "/absolute/path/to/file.csv"])
def test_get_results_security_issue(client, csv_filename):
    response = client.get(url_for('user.get_results', csv_filename=csv_filename))
    assert response.status_code == 400
    assert 'Invalid path' in response.get_json()['error']
