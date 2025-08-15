from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app)

    # Initialize config
    Config.init_app(app)

    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'HTR Flask API'
        }), 200

    # Register blueprints
    from app.routes.upload import upload_bp
    from app.routes.recognition import recognition_bp
    from app.routes.evaluation import evaluation_bp

    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(recognition_bp, url_prefix='/api/recognition')
    app.register_blueprint(evaluation_bp, url_prefix='/api/evaluation')

    return app