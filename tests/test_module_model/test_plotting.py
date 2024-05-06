import numpy as np
import pandas as pd
import pytest


from app.module_model.plotting import cluster_count, process_csv, analyze_data

def test_cluster_count():
    """Test the cluster_count function to ensure it correctly counts occurrences of unique elements."""
    predictions = np.array([1, 1, 2, 3, 1, 2])
    expected_output = {1: 3, 2: 2, 3: 1}
    assert cluster_count(predictions) == expected_output

def test_process_csv(tmpdir):
    """Test the process_csv function to ensure it processes and saves data correctly."""
    # Setup
    csv_content = """Sample,Predicted Cluster,Conf1,Conf2,Conf3,Conf4,Conf5,Conf6,Conf7
    Sample1,1,0.1,0.2,0.3,0.4,0.5,0.6,0.7
    Sample2,2,0.2,0.3,0.4,0.5,0.6,0.7,0.8"""
    csv_path = tmpdir.join("test.csv")
    csv_path.write(csv_content)
    output_dir = tmpdir.mkdir("output")

    # Execute
    result_path = process_csv(str(csv_path), str(output_dir))

    # Validate
    processed_data = pd.read_csv(result_path)
    assert not processed_data.empty
    assert 'Highest Probability Score' in processed_data.columns
    assert processed_data.at[0, 'Highest Probability Score'] == 0.7

def test_analyze_data(tmpdir):
    """Test the analyze_data function to ensure it generates a base64 string of the plot image."""
    # Setup the CSV data for plotting
    csv_content = """Confidence Score Cluster1,Confidence Score Cluster2,Confidence Score Cluster3
    0.8,0.5,0.2
    0.9,0.55,0.25
    0.85,0.6,0.3"""
    csv_path = tmpdir.join("test_plot.csv")
    csv_path.write(csv_content)

    # Execute
    image_base64 = analyze_data(str(csv_path), threshold=0.3)

    # Validate
    assert isinstance(image_base64, str)
    assert image_base64.startswith('iVBORw0KGgo')  # Check if the output looks like a base64 string

# Optional: test for exceptions or error handling
def test_process_csv_no_file():
    """Test process_csv with a non-existent CSV file to ensure it raises an appropriate error."""
    with pytest.raises(FileNotFoundError):
        process_csv("nonexistent.csv", "some_output_dir")

