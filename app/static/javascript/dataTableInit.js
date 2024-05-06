$(document).ready(function () {
    // Initialize the DataTable with dummy data on page load
    window.table = $('#predictionsTable').DataTable({
        "pagingType": "full_numbers", // Enables full pagination control
        "lengthChange": true, // Allows the user to change the number of records per page
        "searching": true, // Enables the search box
        "order": [[3, "asc"]], // Sets the default ordering (in this case based on column 4)
        "info": true, // Shows the 'Showing 1 to X of X entries' information
        "autoWidth": false, // Disables automatic column width calculation
        "data": [{          // Dummy data for initialization
            "Sample": "No Data Loaded",
            "Predicted Cluster": "No Data Loaded",
            "Highest Probability Score": "No Data Loaded"
        }],
        "columns": [    // Defines the columns for the data table
            { "data": "Sample", "title": "Sample" },
            { "data": "Predicted Cluster", "title": "Sample Classification" },
            { "data": "Highest Probability Score", "title": "Highest Probability Score" }
        ]
    });
});