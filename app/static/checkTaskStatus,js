var eventSource = new EventSource("/results_stream/task_id_here");
eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log(data);
    if (data.status === 'SUCCESS' || data.status === 'FAILURE') {
        eventSource.close(); // Close the connection once the task completes
        if (data.status === 'SUCCESS') {
            console.log('Results:', data.result);
            // Update the UI with results
        } else {
            console.error('Task Failed');
        }
    }
};