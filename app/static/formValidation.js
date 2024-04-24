function validateForm() {
    // Gather all radio button groups
    let allGroupsValid = true;
    document.querySelectorAll('div.mb-4').forEach(group => {
        if (!group.querySelector('input[type="radio"]:checked')) {
            allGroupsValid = false; // If any group has no selection, set to false
        }
    });
    
    if (!allGroupsValid) {
        alert('Please select options for all categories.');
        return false;
    }
    
    return true;
}