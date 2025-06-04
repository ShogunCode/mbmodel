import os
import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from app.module_model.model import make_predictions

def test_make_predictions_success():
    """Test making predictions successfully with the model."""
    H = np.array([[0.5, 0.2, 0.3]])
    model_path = 'fake_model_path/model.joblib'
    with patch('os.path.exists') as mock_exists, \
         patch('joblib.load') as mock_load:
        mock_exists.return_value = True
        mock_model = MagicMock()
        mock_model.predict.return_value = np.array([1])
        mock_model.decision_function.return_value = np.array([0.9])
        mock_load.return_value = mock_model
        
        predictions, confidence_scores, input_data = make_predictions(H, model_path)

        mock_exists.assert_called_with(os.path.join(os.getcwd(), model_path))
        assert predictions is not None
        assert confidence_scores is not None
        assert np.array_equal(input_data, H)

def test_make_predictions_file_not_found():
    """Test the behavior when the model file is not found."""
    H = np.array([[0.5, 0.2, 0.3]])
    model_path = 'nonexistent_model_path/model.joblib'
    with patch('os.path.exists', return_value=False), \
         pytest.raises(FileNotFoundError):
        make_predictions(H, model_path)

def test_make_predictions_load_error():
    """Test the model loading error other than FileNotFoundError."""
    H = np.array([[0.5, 0.2, 0.3]])
    model_path = 'fake_model_path/model.joblib'
    with patch('os.path.exists', return_value=True), \
         patch('joblib.load', side_effect=Exception("Load error")), \
         pytest.raises(Exception) as exc_info:
        make_predictions(H, model_path)
    assert "Load error" in str(exc_info.value)

def test_make_predictions_prediction_error():
    """Test prediction errors."""
    H = np.array([[0.5, 0.2, 0.3]])
    model_path = 'fake_model_path/model.joblib'
    with patch('os.path.exists', return_value=True), \
         patch('joblib.load') as mock_load:
        mock_model = MagicMock()
        mock_model.predict.side_effect = Exception("Prediction error")
        mock_load.return_value = mock_model

        with pytest.raises(Exception) as exc_info:
            make_predictions(H, model_path)
    assert "Prediction error" in str(exc_info.value)

