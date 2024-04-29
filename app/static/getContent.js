fetch('static/about.html')
  .then(response => response.text())
  .then(html => {
    document.getElementById('styled-about').innerHTML = html;
  })
  .catch(error => console.error('Error loading the text file:', error));