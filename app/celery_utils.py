# celery_utils.py
from celery import Celery
import eventlet 

celery_app = Celery(__name__)
celery_app.conf.update(
broker_url='redis://localhost:6379/0',
result_backend='redis://localhost:6379/0',
task_serializer='json',
accept_content=['json'],  # accept JSON content only
result_serializer='json'
)

# Function to initialize Celery
def init_celery(app):

    celery_app.conf.update(app.config) 
    
    # Setting a specific worker pool, if needed
    celery_app.conf.update(worker_pool='eventlet')
    
    # Setting the main attribute to the app's import name
    celery_app.main = app.import_name
    
    # Setting the task routes
    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(ContextTask, self).run(*args, **kwargs)
                
    celery_app.Task = ContextTask
    celery_app.autodiscover_tasks(['app.module_data_processing','app.module_user', 'app.module_model'], force=True)