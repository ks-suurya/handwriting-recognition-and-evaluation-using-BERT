import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../uploads')
    RESULTS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../results')
    DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')

    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

    # AI API Keys
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # HTR Pipeline settings
    CONFIG_PATH = os.path.join(DATA_FOLDER, 'config.json')
    WORDS_PATH = os.path.join(DATA_FOLDER, 'words_alpha.txt')

    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.RESULTS_FOLDER, exist_ok=True)