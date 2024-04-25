document.getElementById('uploadButton').onclick = function() {
    // Call validateForm first, and proceed only if it returns true
    if (!validateForm()) {
        return; // Stop the function if validation fails
    }

    var formData = new FormData(document.getElementById('uploadForm'));
    var xhr = new XMLHttpRequest();
    var fileInput = document.getElementById('fileInput');
    var statusText = document.getElementById('statusText');

    xhr.open('POST', '/upload', true);
    xhr.onload = function () {
        if (xhr.status === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.error) {
                statusText.innerHTML = response.error;
            } else {
                document.getElementById('uploadButton').innerText = 'Uploaded ✔';
                document.getElementById('uploadButton').classList.add('bg-green-500');
                document.getElementById('uploadButton').classList.remove('bg-blue-500');
                document.getElementById('uploadButton').disabled = true;
    
                statusText.innerHTML = 'File uploaded successfully. Click "Process Data" to continue.';
                var processButton = document.createElement('button');
                processButton.innerText = 'Process Data';
                processButton.className = 'bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded inline-flex items-center';
                processButton.onclick = function() {
                    processFile(response.file_path);
                };
                document.getElementById('uploadForm').appendChild(processButton);
            }
        } else {
            statusText.innerHTML = 'Upload failed. Server responded with status: ' + xhr.status;
        }
    };
    xhr.onerror = function() {
        statusText.innerHTML = 'Network error, please try again.';
    };
    xhr.send(formData);
};

function validateForm() {
    var fileInput = document.getElementById('fileInput');
    if (fileInput.value == '') {
        alert('Please select a file.');
        return false;
    }
    return true;
}

function processFile(file_path) {
    fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({file_path: file_path})
    })
    .then(response => response.json())
    .then(data => {
        if(data.message) {
            statusText.innerHTML = data.message;
            // Optionally update the UI or display results
        } else if(data.error) {
            statusText.innerHTML = data.error;
            // Handle errors in the UI
        }
    })
    .catch(error => {
        statusText.innerHTML = 'Error processing file: ' + error;
    });
}




