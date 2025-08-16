import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # SQLAlchemy Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS S3 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.environ.get('AWS_REGION')
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')

    # Celery Configuration
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    # Application specific paths (relative to WORKDIR)
    DATA_FOLDER = 'data'
    HTR_PIPELINE_FOLDER = 'htr_pipeline'
    CONFIG_PATH = os.path.join(DATA_FOLDER, 'config.json')
    WORDS_PATH = os.path.join(DATA_FOLDER, 'words_alpha.txt')
