import pytest
from flask import url_for
from app import create_app
from io import BytesIO

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app()
    app.config.update({
        "TESTING": True,  # Update other config values that are test specific if needed
    })
    yield app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_app_is_created(app):
    assert app is not None

def test_app_is_testing(app):
    assert app.config['TESTING']

def test_app_has_correct_blueprints(app):
    assert 'module_user' in app.blueprints
    assert 'module_model' in app.blueprints

def test_celery_is_initialized(app):
    from app.celery_utils import celery_app
    assert celery_app.conf['broker_url'] == app.config['CELERY_BROKER_URL']

def test_index_route(client):
    response = client.get(url_for('module_user.index'))
    assert response.status_code == 200

def test_upload_route(client):
    # Simulating file upload using test client
    data = {
        'file': (BytesIO(b'my file contents'), 'test.txt')
    }
    response = client.post(url_for('module_user.upload_file'), data=data, content_type='multipart/form-data')
    assert response.status_code == 200

def test_process_uploaded_file(client):
    # You would need to adjust this depending on how file_path is typically obtained
    response = client.post(url_for('module_user.process_uploaded_file'), json={'file_path': 'path/to/file'})
    assert response.status_code == 202

def test_get_status_route(client):
    # Assuming there is a valid task_id which should be replaced with a real one during testing
    response = client.get(url_for('module_user.get_status', task_id='dummy_task_id'))
    assert response.status_code == 200

def test_cluster_data_route(client):
    # Assuming there is a valid task_id which should be replaced with a real one during testing
    response = client.get(url_for('module_user.cluster_data', task_id='dummy_task_id'))
    assert response.status_code in [202, 500]

def test_get_results_route(client):
    # Test with a safe file name
    response = client.get(url_for('module_user.get_results', csv_filename='data.csv'))
    assert response.status_code in [200, 404, 500]

def test_trigger_test_task_route(client):
    response = client.get(url_for('module_user.trigger_test_task'))
    assert response.status_code == 200