# __init__.py
from flask import Flask
from app.config import Config
import logging
from app.celery_utils import init_celery, celery_app
from app.module_user.tasks import test_task


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

    init_celery(app)

    with app.app_context():
        from app.module_user.routes import bp as user_bp
        from app.module_model.model import bp as model_bp

        app.register_blueprint(user_bp)
        app.register_blueprint(model_bp)

    return app
