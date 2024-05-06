# test_celery_utils.py
import pytest
from flask import Flask
from app.celery_utils import init_celery, celery_app

@pytest.fixture(scope='module')
def flask_app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        broker_url='redis://localhost:6379/0',
        result_backend='redis://localhost:6379/0'
    )
    init_celery(app)
    return app

@pytest.fixture(scope='module')
def celery_worker(flask_app):
    """Starts a Celery worker with the Flask application context."""
    # We need to import these to patch Celery properly for tests
    from celery.contrib.testing.worker import start_worker
    celery_app.loader.import_task_module('celery.contrib.testing.tasks')
    with start_worker(celery_app, perform_ping_check=False) as worker:
        yield worker
    worker.stop()

def test_celery_task(flask_app, celery_worker):
    """Test if Celery task runs with Flask app context."""
    from celery.contrib.testing.tasks import ping
    with flask_app.app_context():
        task_result = ping.delay()
        assert task_result.get(timeout=10) == 'pong', "Celery task 'ping' failed"
