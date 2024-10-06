import pytest
from unittest.mock import patch, Mock
from flask import Flask
from app.celery_utils import init_celery

# Assume `create_app()` returns a Flask app instance ready for use
from app import create_app 

class TestFlaskApp:
    @pytest.fixture
    def app(self):
        """Create and configure a new app instance for each test."""
        app = create_app()
        app.config.update({
            'TESTING': True,
            'DEBUG': False
        })
        return app

    @pytest.fixture
    def client(self, app):
        """A test client for the app."""
        return app.test_client()

    @pytest.fixture
    def runner(self, app):
        """A test runner for the app's Click commands."""
        return app.test_cli_runner()

    @patch('celery_utils.celery_app')
    def test_init_celery(self, mock_celery_app, app):
        """Test the initialization of Celery without actually connecting to a broker."""
        init_celery(app)
        mock_celery_app.conf.update.assert_called()
        # Check if the Celery app's configuration has been updated with Flask app's config
        assert mock_celery_app.conf.update.called

    # Here, add more tests to test other functionalities of your app that do not involve Celery.

    def test_home_route(self, client):
        """Test the home route."""
        response = client.get('/')
        assert response.status_code == 200
        assert 'Welcome to the Medulloblastoma Classification Tool' in response.data.decode()

# Add more tests for other routes and functionalities of your app as needed.

if __name__ == '__main__':
    pytest.main()
