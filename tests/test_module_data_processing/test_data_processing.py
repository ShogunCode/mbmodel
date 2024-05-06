import os
import numpy as np
import pandas as pd
import pytest

from app.module_data_processing.data_processing import read_data_file, preprocess_data, transform_with_nmf, apply_kmeans, create_csv, generate_json_response

# Mock current_app for all tests
@pytest.fixture
def mock_app(mocker):
    app = mocker.patch('flask.current_app')
    app.config = {'N_METAGENES': 2, 'N_CLUSTERS': 3, 'ML_MODEL_PATH': 'path/to/model'}
    return app

def test_read_data_file_success(tmpdir):
    """Test reading data successfully from a CSV file."""
    csv_content = 'ID_REF,A,B,C\n1,0.1,0.2,0.3\n2,0.4,0.5,0.6'
    file_path = tmpdir.join("data.csv")
    file_path.write(csv_content)

    df = read_data_file(str(file_path))
    assert df is not None
    assert not df.empty

def test_read_data_file_not_found():
    """Test file not found error."""
    with pytest.raises(FileNotFoundError):
        read_data_file('nonexistent.csv')

def test_preprocess_data_empty_input():
    """Test preprocessing with an empty DataFrame."""
    with pytest.raises(ValueError):
        preprocess_data(None)

def test_transform_with_nmf_success():
    """Test NMF transformation."""
    df = pd.DataFrame(np.random.rand(10, 5))
    W, H = transform_with_nmf(df, n_components=3)
    assert W is not None and H is not None
    assert W.shape == (10, 3)
    assert H.shape == (3, 5)

def test_apply_kmeans():
    """Test KMeans clustering."""
    H = np.random.rand(5, 10)
    labels, kmeans = apply_kmeans(H)
    assert labels is not None
    assert len(labels) == 5
    assert kmeans is not None

def test_create_csv(tmpdir, mocker):
    """Test creating a CSV file."""
    predictions = [1, 2, 1]
    confidence_scores = [[0.8, 0.1, 0.1], [0.3, 0.7, 0.0], [0.9, 0.05, 0.05]]
    output_dir = tmpdir.mkdir("output")
    filename = 'test_output.csv'

    full_path = create_csv(predictions, confidence_scores, filename=str(output_dir.join(filename)))
    assert os.path.exists(full_path)
    with open(full_path, 'r') as f:
        lines = f.readlines()
        assert len(lines) == 4  # Header plus three data rows

def test_generate_json_response():
    """Test generating a JSON response."""
    confidences = np.array([[0.8, 0.2], [0.6, 0.4]])
    response = generate_json_response(confidences)
    assert 'Cluster' in response
    assert 'Confidence Scores' in response

# Optionally: Additional tests for other utilities, error handling, and edge cases

@pytest.mark.parametrize("file_path,expected_exception", [
    ("path/to/invalid_file.txt", FileNotFoundError),
    ("path/to/empty_file.csv", pd.errors.EmptyDataError),
    ("path/to/wrong_format.txt", pd.errors.ParserError),
])
def test_read_data_file_errors(file_path, expected_exception):
    """Test various errors in read_data_file."""
    with pytest.raises(expected_exception):
        read_data_file(file_path)
