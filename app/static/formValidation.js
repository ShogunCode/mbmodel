function validateForm() {
    let allGroupsValid = true;
    document.querySelectorAll('div.mb-4').forEach(group => {
        const radioChecked = group.querySelector('input[type="radio"]:checked');
        console.log(radioChecked); // Check which radio button is selected
        if (!radioChecked) {
            allGroupsValid = false; // If any group has no selection, set to false
            console.log('No selection in group:', group); // Identify the problematic group
        }
    });
    
    if (!allGroupsValid) {
        alert('Please select options for all categories.');
        return false;
    }
    
    return true;
}