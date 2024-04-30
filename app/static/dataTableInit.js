$(document).ready(function () {
    // Initialize the DataTable with dummy data on page load
    window.table = $('#predictionsTable').DataTable({
        "data": [{
            "Sample": "No Data Loaded",
            "Predicted Cluster": "No Data Loaded",
            "Highest Probability Score": "No Data Loaded"
        }],
        "columns": [
            { "data": "Sample", "title": "Sample" },
            { "data": "Predicted Cluster", "title": "Predicted Cluster" },
            { "data": "Highest Probability Score", "title": "Highest Probability Score" }
        ]
    });
});