function processFile(file_path) {
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({file_path: file_path})
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.task_id) {
            // Assuming server returns a task ID for polling
            statusText.innerHTML = 'Processing started...';
            pollForResult(data.task_id);
        } else if (data.error) {
            statusText.innerHTML = data.error;
        }
    })
    .catch(error => {
        statusText.innerHTML = 'Error processing file: ' + error.message;
    });
}

function pollForResult(taskId) {
    const intervalId = setInterval(() => {
        fetch(`/results/${taskId}`)  // Corrected endpoint
        .then(response => response.json())
        .then(data => {
            if (data.state === 'completed') {
                clearInterval(intervalId);
                updatePlots(data.result);  // Assume updatePlots handles the plot data
                statusText.innerHTML = 'Results are ready below.';
            } else if (data.state === 'error') {
                clearInterval(intervalId);
                statusText.innerHTML = 'Error during processing: ' + data.status;
            }
        })
        .catch(error => {
            clearInterval(intervalId);
            statusText.innerHTML = 'Error fetching results: ' + error.message;
        });
    }, 3000); // Poll every 3 seconds
}
