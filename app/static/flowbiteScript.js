document.addEventListener('DOMContentLoaded', function () {
    const tabs = document.querySelectorAll('[role="tab"]');
    const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

    // Options for active and inactive classes
    const options = {
        activeClasses: 'text-custom-red hover:text-custom-red dark:text-custom-red dark:hover:text-custom-red border-custom-red dark:border-custom-red',
        inactiveClasses: 'dark:border-transparent text-gray-500 hover:text-gray-600 dark:text-gray-400 border-gray-100 hover:border-gray-300 dark:border-gray-700 dark:hover:text-gray-300'
    };

    function changeTab(event) {
        const targetTab = event.target;
        console.log("Target tab:", targetTab);
        console.log("Data-tabs-target attribute:", targetTab.getAttribute('data-tabs-target'));

        const targetPanel = document.querySelector(targetTab.getAttribute('data-tabs-target'));
        console.log("Target panel element:", targetPanel);

        if (!targetPanel) {
            console.error("No element found for data-tabs-target:", targetTab.getAttribute('data-tabs-target'));
            return; // Early return to prevent errors
        }

        tabPanels.forEach(panel => {
            panel.classList.add('hidden');
        });

        tabs.forEach(tab => {
            tab.setAttribute('aria-selected', 'false');
            tab.classList.remove(...options.activeClasses.split(' '));
            tab.classList.add(...options.inactiveClasses.split(' '));
        });

        targetTab.setAttribute('aria-selected', 'true');
        targetTab.classList.add(...options.activeClasses.split(' '));
        targetTab.classList.remove(...options.inactiveClasses.split(' '));
        targetPanel.classList.remove('hidden');
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', changeTab);
    });

    // Automatically click on the first tab to make it active
    if (tabs.length > 0) {
        tabs[0].click();
    }
});
