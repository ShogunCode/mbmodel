import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from app import create_app

class TestFlaskApp(unittest.TestCase):

    def setUp(self):
        """Setup the Flask app for testing."""
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

    def tearDown(self):
        """Pop the context after the test."""
        self.app_context.pop()

    @patch('app.celery_utils.celery_app.task')
    @patch('app.module_data_processing.data_processing.read_data_file')
    @patch('app.module_data_processing.data_processing.preprocess_data')
    @patch('app.module_data_processing.data_processing.transform_with_nmf')
    @patch('app.module_model.model.make_predictions')
    @patch('app.module_model.plotting.analyze_data')
    @patch('app.module_data_processing.data_processing.create_csv')
    def test_process_file_async(self, mock_create_csv, mock_analyze_data, mock_make_predictions, mock_transform_with_nmf, mock_preprocess_data, mock_read_data_file, mock_celery_task):
        # Setup mocks
        mock_read_data_file.return_value = "raw_data"
        mock_preprocess_data.return_value = "preprocessed_data"
        mock_transform_with_nmf.return_value = (MagicMock(), MagicMock())
        mock_make_predictions.return_value = ("predictions", "confidence_scores", None)
        mock_analyze_data.return_value = "plot_path"

        from app.celery_utils import process_file_async

        # Execute the function
        result = process_file_async("dummy_path")

        # Assertions to ensure each function was called
        mock_read_data_file.assert_called_once_with("dummy_path")
        mock_preprocess_data.assert_called_once_with("raw_data")
        mock_transform_with_nmf.assert_called_once_with("preprocessed_data", self.app.config['N_METAGENES'])
        mock_make_predictions.assert_called_once_with(MagicMock().T, self.app.config['ML_MODEL_PATH'])
        mock_create_csv.assert_called_once_with("predictions", "confidence_scores", filename=f'{MagicMock().request.id}.csv')
        mock_analyze_data.assert_called_once_with(self.app.config['CSV_OUTPUT_DIR'] + f'{MagicMock().request.id}.csv')

        # Check the output format
        self.assertIsInstance(result, dict)

if __name__ == '__main__':
    unittest.main()
