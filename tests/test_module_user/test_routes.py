import unittest
from unittest.mock import patch
from flask_testing import TestCase
from app import create_app
import pandas as pd

class TestFlaskRoutes(TestCase):
    def create_app(self):
        """Create and configure a new app instance for each test."""
        app = create_app()
        app.config['TESTING'] = True
        return app

    def test_index_route(self):
        """Test the index route."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Welcome', response.data.decode())

    @patch('app.module_user.file_utils.save_uploaded_file')
    def test_upload_file(self, mock_save_uploaded_file):
        """Test file upload."""
        mock_save_uploaded_file.return_value = ('/path/to/file', None, 200)
        response = self.client.post('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn('File uploaded successfully', response.data.decode())

    @patch('app.module_user.tasks.process_file_async.delay')
    def test_process_uploaded_file(self, mock_process_file_async):
        """Test processing an uploaded file."""
        mock_process_file_async.return_value.id = '1234'
        response = self.client.post('/process', json={'file_path': '/path/to/file'})
        self.assertEqual(response.status_code, 202)
        self.assertIn('File processing initiated', response.data.decode())

    @patch('app.module_user.tasks.process_file_async.AsyncResult')
    def test_get_status(self, mock_AsyncResult):
        """Test getting the status of a processing task."""
        mock_task = mock_AsyncResult.return_value
        mock_task.state = 'SUCCESS'
        mock_task.result = {'some': 'data'}
        response = self.client.get('/status/1234')
        self.assertEqual(response.status_code, 200)
        self.assertIn('SUCCESS', response.data.decode())

    @patch('os.path.isfile')
    @patch('pandas.read_csv')
    def test_get_results(self, mock_read_csv, mock_isfile):
        """Test fetching results from a CSV file."""
        mock_isfile.return_value = True
        mock_read_csv.return_value = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        response = self.client.get('/get-results/valid_file.csv')
        self.assertEqual(response.status_code, 200)
        self.assertIn('A', response.data.decode())

if __name__ == '__main__':
    unittest.main()
