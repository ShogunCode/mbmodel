# Medulloblastoma Classification - Machine Learning Web Application - QUB MSc Dissertation 👨‍💻

## Overview 🔍
This repository contains my code for a web-based application designed to classify **Medulloblastoma** subtypes using **DNA methylation**. This project was completed as part of my MSc in Software Development at Queen’s University Belfast and serves as a tool for medical professionals and researchers to aid in the diagnosis and treatment of this complex brain tumor.

The application uses machine learning to provide accurate subtype classification, offering personalised treatment for enhanced clinical outcomes in oncology.

### Key Features 💻

- **Web Application**: Built using **Flask**, providing a user-friendly interface for professionals to upload DNA methylation data.
- **Machine Learning Model**: A **Support Vector Machine (SVM)** model with 97.5% accuracy was implemented to classify the MB subtypes.
- **Dimensionality Reduction**: Utilised **Non-Negative Matrix Factorisation (NMF)** and **k-means clustering** to handle high-dimensional data. Original data == 428 * 450,000 (428 Samples * 450,000~ features).
- **t-SNE Visualisation**: Provides 2D and 3D visualisations for exploratory data analysis.
- **Asynchronous Task Management**: **Celery** and **Redis** handle computationally intensive tasks in the background, ensuring a responsive user experience.

## Project Motivation 🧠

Medulloblastoma (MB) is the most common malignant pediatric brain tumor, and its biological complexity poses challenges in diagnosis and treatment. By using DNA methylation data, this project seeks to improve diagnostic precision and contribute to personalised medicine, by providing tools that offer a better insight into MB subtypes.

## Application Architecture 🛠️

The system architecture is designed to be modular:

1. **Frontend**: A user-friendly web interface for uploading and visualising the results of data analysis.
2. **Backend**: Flask handles requests and serves machine learning predictions. 
   - **Routing**: Managed by `routes.py`, with endpoints for file upload, processing and results retrieval.
3. **Machine Learning Pipeline**:
   - Data uploaded is processed using **Pandas** and cleaned.
   - **Dimensionality reduction** is performed using **NMF** to extract metagenes.
   - Classification is handled by a pre-trained **SVM model**, producing subtype predictions.
   - Results are visualised using **Matplotlib** for confidence interval plots and **t-SNE** for cluster mapping.
4. **Task Management**: **Celery** and **Redis** manage asynchronous tasks, allowing the model to process large datasets without blocking user interaction.

### Core Technologies 🐍

- **Python** (Flask, Celery, Pandas, NumPy, Scikit-learn)
- **Redis** for task queuing
- **Chart.js** and **Matplotlib** for data visualisation
- **Tailwind CSS** for responsive UI design

## Usage 🖱️

-  **Upload Data**: Upload DNA methylation data in .txt or .csv format through the web interface.
-  **Process Data**: The application will process the data and classify it using the machine learning model.
-  **Visualise Results**: The results can be visualised in a confidence box plot and classified samples can be downloaded in .csv format.
-  **Download Results**: You can download the processed results as a CSV file for further analysis.

## Technical Challenges 🚧

*During the development of this project, several challenges were encountered*:
1. **Handling High Dimensionality**: Processing 450,000 features per sample required extensive dimensionality reduction. NMF was chosen as an effective solution to simplify data while preserving relevant biological information.
2. **Efficient Asynchronous Processing**: Large datasets often led to slow performance. Using Celery with Redis allows for significantly improved responsiveness by handling tasks in the background without blocking user interaction.
3. **Model Accuracy and Validation**: Achieving high classification accuracy while reducing overfitting was a critical task. Multiple models were tested, and an SVM model was selected for its 97.5% accuracy.
4. **Data Security**: Since this project deals with sensitive data, validation checks were put in place to ensure file integrity and proper formatting.

## Future Work 📈

- **Deep Learning Integration**: Expand the classification model to include deep learning methods such as Convolutional Neural Networks (CNNs) for image-based classification.
- **Ensemble Models**: Implement an ensemble of models that combines image and tabular data for a more robust diagnostic tool.

## Acknowledgments 🤝
**I would like to express my gratitude to Dr. Reza Rafiee for the invaluable guidance and support throughout this project. Special thanks to my family and friends for their constant support during this journey.**
