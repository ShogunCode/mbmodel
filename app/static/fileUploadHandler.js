document.getElementById('uploadButton').addEventListener('click', function(event) {
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
                processButton.onclick = function(event) {
                    event.preventDefault(); // This line may be redundant if the button type is set to 'button'
                    processFile(response.file_path);
};
document.getElementById('uploadForm').appendChild(processButton);
            }
        } else {
            statusText.textContent = 'Upload failed. Server responded with status: ' + xhr.status;
            uploadButton.disabled = false; // Allow retrying if there was an error
        }
    };
    xhr.onerror = function() {
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
    processXhr.onload = function() {
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

    processXhr.onerror = function() {
        console.error("Network error during processing.");
        statusText.textContent = 'Network error during processing.';
    };

    processXhr.send(JSON.stringify({ file_path: file_path }));
}

function pollForTaskCompletion(taskId) {
    var statusText = document.getElementById('statusText');
    var checkStatus = function() {
        var statusXhr = new XMLHttpRequest();
        statusXhr.open('GET', '/status/' + taskId, true);
        statusXhr.onload = function() {
            if (statusXhr.status === 200) {
                var response = JSON.parse(statusXhr.responseText);
                console.log("Task status response: ", response);
                if (response.state === 'SUCCESS') {
                    // Handle success
                    statusText.textContent = 'Processing completed successfully.';
                    // Process the response.result as needed
                } else if (response.state === 'FAILURE') {
                    // Handle failure
                    statusText.textContent = 'Processing failed.';
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

        statusXhr.onerror = function() {
            console.error("Network error while checking task status.");
            statusText.textContent = 'Network error while checking task status.';
        };

        statusXhr.send();
    };
    
    // Start the polling process
    checkStatus();
}