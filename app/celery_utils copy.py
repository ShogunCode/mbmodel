# celery_utils.py
from celery import Celery

def make_celery(app_name, broker, backend):
    celery = Celery(app_name, broker=broker, backend=backend)
    celery.conf.update(task_serializer='json', accept_content=['json'], result_serializer='json')
        
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.autodiscover_tasks(['app.module_user', 'app.module_model'])  # Adjust according to your package structure
    return celery

celery_app = make_celery('app', 'redis://localhost:6379/0', 'redis://localhost:6379/0')
