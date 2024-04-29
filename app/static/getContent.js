fetch('static/about.html')
  .then(response => response.text())
  .then(html => {
    document.getElementById('styled-about').innerHTML = html;
    initializeTabs();
  })
  .catch(error => console.error('Error loading the text file:', error));

  function initializeTabs() {
    const tabs = document.querySelectorAll('[role="tab"]');
    const tabPanels = Array.from(document.querySelectorAll('[role="tabpanel"]'));

    tabs.forEach(tab => {
        tab.addEventListener('click', changeTab);
    });

    if(tabs.length > 0) {
        tabs[0].click();
    }
}