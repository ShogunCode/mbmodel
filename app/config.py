class Config:
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'csv', 'txt'}
    N_CLUSTERS = 7
    N_METAGENES = 6
    MODEL_FOLDER = 'app/module_model'
    ML_MODEL_PATH = 'app/module_model/svm_model.joblib'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    