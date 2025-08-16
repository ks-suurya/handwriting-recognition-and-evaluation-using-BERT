import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate
from celery import Celery

# 1. Create the Celery instance at the module level
celery = Celery(__name__, broker=Config.CELERY_BROKER_URL)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)

    # 2. Update Celery config from the Flask app config
    celery.conf.update(app.config)

    # 3. Subclass Celery's Task to automatically add the app context
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask

    # 4. Import and register Blueprints inside the factory
    from app.routes.students import students_bp
    from app.routes.categories import categories_bp
    from app.routes.model_answers import model_answers_bp
    from app.routes.submissions import submissions_bp

    app.register_blueprint(students_bp, url_prefix='/api/students')
    app.register_blueprint(categories_bp, url_prefix='/api/categories')
    app.register_blueprint(model_answers_bp, url_prefix='/api/model-answers')
    app.register_blueprint(submissions_bp, url_prefix='/api/submissions')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200

    return app
