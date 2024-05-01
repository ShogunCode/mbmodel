document.getElementById('uploadButton').addEventListener('click', function (event) {
    event.preventDefault(); // Prevent the default form submission

    // Call validateForm first, and proceed only if it returns true
    if (!validateForm()) {
        return; // Stop the function if validation fails
    }

    var formData = new FormData(document.getElementById('uploadForm'));
    var xhr = new XMLHttpRequest();
    var statusText = document.getElementById('statusText');

    // Disable the upload button to prevent multiple submissions
    var uploadButton = document.getElementById('uploadButton');
    uploadButton.disabled = true;

    xhr.open('POST', '/upload', true);
    xhr.onload = function () {
        // Log the entire response object for debugging
        console.log("Response received: ", xhr);

        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            console.log("Parsed response: ", response); // Log the parsed response
            if (response.error) {
                statusText.textContent = response.error;
            } else {
                uploadButton.textContent = 'Uploaded ✔';
                uploadButton.classList.add('bg-green-500');
                uploadButton.classList.remove('bg-blue-500');

                statusText.textContent = 'File uploaded successfully. Click "Process Data" to continue.';
                var processButton = document.createElement('button');
                processButton.textContent = 'Process Data';
                processButton.className = 'bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center';
                processButton.type = 'button'; // This ensures the button does not submit a form
                processButton.onclick = function (event) {
                    // Prevent the default form submission behavior
                    event.preventDefault();

                    // Hide the Process Data button
                    processButton.style.display = 'none';

                    // Create a loading bar element (or any other indicator you wish to use)
                    var loadingBar = document.createElement('div');
                    loadingBar.className = 'loading-bar'; // Add appropriate styles in your CSS
                    loadingBar.textContent = 'Processing...'; // Text or any loading animation

                    // Append the loading bar to the form
                    document.getElementById('uploadForm').appendChild(loadingBar);

                    // Call the function that starts the processing of the file
                    processFile(response.file_path);
                };
                document.getElementById('uploadForm').appendChild(processButton);
            }
        } else {
            statusText.textContent = 'Upload failed. Server responded with status: ' + xhr.status;
            uploadButton.disabled = false; // Allow retrying if there was an error
        }
    };
    xhr.onerror = function () {
        console.error("Network error occurred.");
        statusText.textContent = 'Network error, please try again.';
        // Re-enable the upload button in case of error so the user can try again
        uploadButton.disabled = false;
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
    var xhr = new XMLHttpRequest();
    xhr.open('GET', '/get-results/' + encodeURIComponent(filename), true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var data = JSON.parse(xhr.responseText);
            if (window.table) {
                window.table.clear();
                window.table.rows.add(data);
                window.table.draw();
            } else {
                console.error("DataTable is not initialized yet.");
            }
        } else {
            console.error("Failed to get result data: ", xhr.responseText);
        }
    };
    xhr.onerror = function () {
        console.error("Network error while fetching results.");
    };
    xhr.send();
}

function updatePieChart(taskId) {
    fetch('/cluster-data/' + taskId)
        .then(response => response.json())
        .then(data => {
            console.log("Received data:", data);  // Debug to see the received data
            console.log("Type of data:", typeof data);

            const ctx = document.getElementById('pieChart').getContext('2d');

            // Generate labels only for existing keys
            const labels = Object.keys(data)
                                 .filter(key => data[key] !== undefined && data[key] !== null)  // Ensure only valid data is used
                                 .map(key => `Cluster ${key}`);  // Map to "Cluster X" format

            console.log("Labels:", labels);  // Log the labels to verify

            const values = Object.values(data).filter(value => value !== undefined && value !== null);
            console.log("Values:", values);  // Log the values to verify

            const backgroundColors = generateColors(labels.length);  // Generate colors based on the number of labels

            if (window.pieChart instanceof Chart) {
                window.pieChart.destroy();  // Safely destroy existing chart
            }

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
        })
        .catch(error => console.error('Error fetching pie chart data:', error));
}

// Function to generate colors dynamically
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        // Generate a random color
        const red = Math.floor(Math.random() * 256);
        const green = Math.floor(Math.random() * 256);
        const blue = Math.floor(Math.random() * 256);
        colors.push(`rgba(${red}, ${green}, ${blue}, 0.2)`);
    }
    return colors;
}

function pollForTaskCompletion(taskId) {
    var statusText = document.getElementById('statusText');
    var downloadButton = null; // Declare download button here to ensure it is accessible throughout the function
    var downloadContainer = document.getElementById('downloadButtonContainer'); // Define the container where the download button will be appended
    var checkStatus = function () {
        var statusXhr = new XMLHttpRequest();
        statusXhr.open('GET', '/status/' + taskId, true);
        statusXhr.onload = function () {
            if (statusXhr.status === 200) {
                var response = JSON.parse(statusXhr.responseText);
                console.log("Task status response: ", response);
                if (response.state === 'SUCCESS') {
                    // Remove the loading bar
                    var loadingBar = document.querySelector('.loading-bar'); // Make sure this selector matches your loading bar's class or id
                    if (loadingBar) {
                        loadingBar.remove();
                    }
                    if (response.result && response.result.processed_file) {
                        window.updateTable(response.result.processed_file);

                        // Check if the button does not exist, then create it
                        if (!downloadButton) {
                            downloadButton = document.createElement('a');
                            downloadButton.textContent = 'Download Results';
                            downloadButton.className = 'download-button';
                            downloadContainer.appendChild(downloadButton); // Ensure this element is correctly targeted
                        }
                        // Update the download button's link with the new filename
                        downloadButton.href = response.result.processed_file;
                    } else {
                        console.error("Expected processed CSV filename not found in response: ", response.result);
                        statusText.textContent = 'Data processed but no results file to display.';
                    }
                    updatePieChart(taskId); // Assuming response.result contains data for the pie chart
                    statusText.textContent = 'Pie Chart Update completed successfully.';
                    // Handle success, display image or result
                    const plotImage = document.getElementById('plotImage');
                    console.log("Image data: ", response.result.image);
                    if (response.result && response.result.image) {
                        plotImage.src = 'data:image/png;base64,' + response.result.image;
                        statusText.textContent = 'Data processed successfully.';
                    } else {
                        statusText.textContent = 'Data processed but no image to display.';
                        console.error("Expected image data not found in response: ", response.result);
                    }
                } else if (response.state === 'FAILURE') {
                    // Handle failure, display error message
                    statusText.textContent = 'Task failed with error: ' + response.status;
                } else {
                    // Continue polling
                    console.log('Processing still underway...');
                    setTimeout(checkStatus, 5000); // Poll every 5 seconds
                }
            } else {
                console.error("Failed to check task status: ", statusXhr.responseText);
                statusText.textContent = 'Failed to check task status.';
            }
        };

        statusXhr.onerror = function () {
            console.error("Network error while checking task status.");
            statusText.textContent = 'Network error while checking task status.';
        };

        statusXhr.send();
    };

    // Start the polling process
    checkStatus();
}