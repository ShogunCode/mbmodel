import pytest
from unittest.mock import patch
from app.module_user.tasks import test_task, process_file_async

@pytest.fixture
def app():
    from app import create_app
    return create_app()

def test_test_task():
    """Test the simple test task to ensure it runs and returns 'Success'."""
    result = test_task.apply().get()
    assert result == "Success"

@patch('app.module_data_processing.data_processing.read_data_file')
@patch('app.module_data_processing.data_processing.preprocess_data')
@patch('app.module_data_processing.data_processing.transform_with_nmf')
@patch('app.module_model.model.make_predictions')
@patch('app.module_data_processing.data_processing.create_csv')
@patch('app.module_model.plotting.cluster_count')
@patch('app.module_model.plotting.process_csv')
@patch('app.module_model.plotting.analyze_data')
def test_process_file_async(mock_analyze_data, mock_process_csv, mock_cluster_count, mock_create_csv, mock_make_predictions, mock_transform_with_nmf, mock_preprocess_data, mock_read_data_file, app):
    """Test the complex file processing task."""
    mock_read_data_file.return_value = 'raw data'
    mock_preprocess_data.return_value = 'preprocessed data'
    mock_transform_with_nmf.return_value = ('W', 'H')
    mock_make_predictions.return_value = ('predictions', 'confidence_scores', None)
    mock_create_csv.return_value = None
    mock_cluster_count.return_value = {'count': 3}
    mock_process_csv.return_value = 'processed_filename'
    mock_analyze_data.return_value = 'plot_path'

    with app.app_context():
        result = process_file_async.apply(args=['/path/to/mockfile']).get()
        assert result == {
            'processed_file': 'processed_filename',
            'image': 'plot_path',
            'cluster_count': {'count': 3}
        }


def test_process_file_async_failure(mock_read_data_file, app):
    """Test error handling in the file processing task."""
    mock_read_data_file.side_effect = Exception("Failed to read file")
    with app.app_context():
        with pytest.raises(Exception) as exc_info:
            process_file_async.apply(args=['/path/to/mockfile']).get()
        assert "Failed to read file" in str(exc_info.value)
