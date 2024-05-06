document.getElementById('uploadButton').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default form submission behavior

    var formData = new FormData(document.getElementById('uploadForm'));
    var xhr = new XMLHttpRequest();
    var statusText = document.getElementById('statusText');
    var uploadButton = document.getElementById('uploadButton');
    var processButton = document.getElementById('processButton'); // Move this line here for better structure

    // Disable the upload button to prevent multiple submissions
    uploadButton.disabled = true;

    xhr.open('POST', '/upload', true);
    xhr.onload = function () {
        console.log("Response received: ", xhr);
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log("Parsed response: ", response);
            if (response.error) {
                statusText.textContent = response.error;
                uploadButton.disabled = false; // Re-enable the upload button if there is an error
            } else {
                uploadButton.textContent = 'Uploaded ✔';
                uploadButton.classList.add('bg-green-500');
                uploadButton.classList.remove('bg-gray-300');

                statusText.textContent = 'File uploaded successfully. Click "Process Data" to continue.';
                processButton.classList.remove('hidden'); // Unhide the Process Data button

                processButton.onclick = function () {
                    processButton.classList.add('hidden'); // Optionally re-hide the button
                    statusText.textContent = 'Processing...'; // Update status text

                    // You may want to disable the button here to prevent multiple processing requests
                    processButton.disabled = true;

                    // Call the function that handles the actual processing
                    processFile(response.file_path);
                };
            }
        } else {
            statusText.textContent = 'Failed to upload file.';
            uploadButton.disabled = false; // Re-enable the upload button if there is a server error
        }
    };

    xhr.onerror = function () {
        console.error("Network error occurred.");
        statusText.textContent = 'Network error, please try again.';
        uploadButton.disabled = false; // Re-enable the upload button in case of network error
    };

    xhr.send(formData);
});

function processFile(file_path) {
    console.log("Processing file at path: ", file_path);
    var statusText = document.getElementById('statusText');

    var processXhr = new XMLHttpRequest();
    processXhr.open('POST', '/process', true);
    processXhr.setRequestHeader('Content-Type', 'application/json');
    processXhr.onload = function () {
        if (processXhr.status === 202) {
            var response = JSON.parse(processXhr.responseText);
            console.log("Processing initiated response: ", response);
            statusText.textContent = 'Processing initiated. Please wait...';
            // Begin polling for the process status
            pollForTaskCompletion(response.task_id);
        } else {
            console.error("Processing error: ", processXhr.responseText);
            statusText.textContent = 'Error during processing.';
        }
    };

    processXhr.onerror = function () {
        console.error("Network error during processing.");
        statusText.textContent = 'Network error during processing.';
    };

    processXhr.send(JSON.stringify({ file_path: file_path }));
}

function updateTable(csvFilename) {
    // Extract the filename if a path is given
    var filename = csvFilename.split('/').pop();  // This will get only the filename, stripping any path

    // Ensure filename is present before making the request
    if (!filename) {
        console.error("No filename provided for updateTable.");
        return;
    }

    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get-results/' + encodeURIComponent(filename), true);

    xhr.onload = function () {
        if (xhr.status === 200) {
            try {
                var data = JSON.parse(xhr.responseText); // Safely parse the response
                if (window.table) {
                    window.table.clear();
                    window.table.rows.add(data); // Assuming 'data' is in the correct format for DataTables
                    window.table.draw();
                } else {
                    console.error("DataTable is not initialized yet.");
                }
            } catch (e) {
                console.error("Error parsing server response:", e);
            }
        } else {
            console.error("Failed to get result data: ", xhr.status, xhr.statusText);
        }
    };

    xhr.onerror = function () {
        console.error("Network error while fetching results.");
    };

    xhr.send();
}

function updatePieChart(data) {
    console.log("Received pie chart data:", data);
    const ctx = document.getElementById('pieChart').getContext('2d');
    if (!ctx) {
        console.error("Canvas context not accessible");
        return;
    }
    
    // Log canvas size for debugging
    console.log("Canvas size:", ctx.canvas.width, "x", ctx.canvas.height);
    
    if (window.pieChart instanceof Chart) {
        window.pieChart.destroy();  // Destroy existing chart instance if exists
        console.log("Existing chart instance destroyed.");
    }

    const labels = Object.keys(data).map(key => `Cluster ${key}`);
    const values = Object.values(data);
    
    console.log("Labels:", labels);
    console.log("Values:", values);

    const backgroundColors = generateColors(labels.length);
    console.log("Background colors generated for chart:", backgroundColors);

    try {
        window.pieChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Number of Samples per Cluster',
                    data: values,
                    backgroundColor: backgroundColors,
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        enabled: true
                    }
                }
            }
        });

        console.log("Pie chart created successfully.");
    } catch (error) {
        console.error("Error creating pie chart:", error);
    }
    
    // Optionally force a resize if needed
    if (window.pieChart) {
        window.pieChart.resize();
    }
}

// Function to generate colors dynamically
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const red = Math.floor(Math.random() * 256);
        const green = Math.floor(Math.random() * 256);
        const blue = Math.floor(Math.random() * 256);
        colors.push(`rgba(${red}, ${green}, ${blue}, 0.7)`);  // Changed opacity for better visibility
    }
    return colors;
}

function updateChartStats(data) {
    const statsDiv = document.getElementById('chartStats');
    const totalSamples = Object.values(data).reduce((acc, curr) => acc + curr, 0); // Summing all the values
    statsDiv.textContent = `Total Samples: ${totalSamples}`; // Displaying total number of samples
}

function updateNewChartStats(data) {
    const newStatsDiv = document.getElementById('newChartStats');
    const totalSamples = Object.values(data).reduce((acc, curr) => acc + curr, 0); // Calculate the total samples
    newStatsDiv.textContent = `Total Samples: ${totalSamples}`; // Update text content of the new stats div
}

function pollForTaskCompletion(taskId) {
    const statusText = document.getElementById('statusText');
    const downloadContainer = document.getElementById('downloadButtonContainer');
    let downloadButton = null;

    const handleSuccess = (response) => {
        removeLoadingBar();
        if (response.result) {
            // Check if processed file data is available and update the table
            if (response.result.processed_file) {
                updateTable(response.result.processed_file);
                updateDownloadButton(response, downloadContainer, downloadButton);
            } else {
                console.error("Expected processed CSV filename not found in response.");
                statusText.textContent = 'Data processed but no results file to display.';
            }

            // Check if pie chart data is available and update the pie chart
            if (response.result.cluster_count) {
                updatePieChart(response.result.cluster_count); // Update the pie chart
                updateChartStats(response.result.cluster_count); // Update the chart stats
                updateNewChartStats(response.result.cluster_count); // Update the new chart stats
            } else {
                console.error("Pie chart data not found in response.");
            }

            // Update the status and image if available
            updateStatusAndImage(response);
        } else {
            console.error("Invalid response format:", response);
            statusText.textContent = 'Error processing the data. Invalid response format.';
        }
    };

    const handleFailure = (response) => {
        statusText.textContent = 'Task failed with error: ' + response.status;
    };

    const continuePolling = () => {
        console.log('Processing still underway...');
        setTimeout(checkStatus, 2000); // Poll every 5 seconds
    };

    const checkStatus = () => {
        var statusXhr = new XMLHttpRequest();
        statusXhr.open('GET', '/status/' + taskId, true);
        statusXhr.onload = () => {
            if (statusXhr.status === 200) {
                var response = JSON.parse(statusXhr.responseText);
                console.log("Task status response: ", response);
                if (response.state === 'SUCCESS') {
                    handleSuccess(response);
                } else if (response.state === 'FAILURE') {
                    handleFailure(response);
                } else {
                    continuePolling();
                }
            } else {
                console.error("Failed to check task status: ", statusXhr.responseText);
                statusText.textContent = 'Failed to check task status.';
            }
        };
        statusXhr.onerror = () => {
            console.error("Network error while checking task status.");
            statusText.textContent = 'Network error while checking task status.';
        };
        statusXhr.send();
    };

    checkStatus(); // Start the polling process
}

function processStatusXhrLoad(xhr, onSuccess, onFailure, onContinue) {
    if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText);
        console.log("Task status response: ", response);
        if (response.state === 'SUCCESS') {
            onSuccess(response);
        } else if (response.state === 'FAILURE') {
            onFailure(response);
        } else {
            onContinue();
        }
    } else {
        console.error("Failed to check task status: ", xhr.responseText);
        document.getElementById('statusText').textContent = 'Failed to check task status.';
    }
}

function removeLoadingBar() {
    const loadingBar = document.querySelector('.loading-bar');
    if (loadingBar) {
        loadingBar.remove();
    }
}

let downloadButton = null; // Moved to a higher scope outside of the function

function updateDownloadButton(response, downloadContainer) {
    if (response.result && response.result.processed_file) {
        if (!downloadButton) {
            downloadButton = document.createElement('a');
            downloadButton.textContent = 'Download Results';
            downloadButton.className = 'download-button';
            downloadContainer.appendChild(downloadButton);
        }
        downloadButton.href = response.result.processed_file;
    } else {
        console.error("Expected processed CSV filename not found in response: ", response.result);
        document.getElementById('statusText').textContent = 'Data processed but no results file to display.';
    }
}

function updatePieChartWithResponse(response) {
    // Check if 'cluster_count' data is available in the response
    if (response.result && response.result.cluster_count) {
        updatePieChart(response.result.cluster_count);  // Pass the cluster count data to the pie chart
    } else {
        console.error("Pie chart data not found in response.");
        // Optionally, update the UI to inform the user that the pie chart data is not available.
    }
}

// Utility to update the status text and image display
function updateStatusAndImage(response) {
    const plotImage = document.getElementById('plotImage');
    if (response.result && response.result.image) {
        plotImage.src = 'data:image/png;base64,' + response.result.image;
        statusText.textContent = 'Data processed successfully.';
    } else {
        statusText.textContent = 'Data processed but no image to display.';
        console.error("Expected image data not found in response.");
    }
}

function handleNetworkError() {
    console.error("Network error while checking task status.");
    document.getElementById('statusText').textContent = 'Network error while checking task status.';
}