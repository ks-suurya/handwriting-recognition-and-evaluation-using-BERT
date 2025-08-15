from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from app.utils.validators import validate_image_file
import logging

logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)


@upload_bp.route('/image', methods=['POST'])
def upload_image():
    """
    Upload an image file for OCR processing.

    Expected: multipart/form-data with 'file' field

    Returns:
    {
        "success": true,
        "file_id": "unique-file-identifier",
        "filename": "original-filename.jpg",
        "message": "File uploaded successfully"
    }
    """
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file part in request'
            }), 400

        file = request.files['file']

        # Validate file
        is_valid, message = validate_image_file(file)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400

        # Generate unique file ID
        file_id = str(uuid.uuid4())
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{file_id}.{file_extension}"

        # Save file
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        logger.info(f"File uploaded: {filename}")

        return jsonify({
            'success': True,
            'file_id': file_id,
            'filename': file.filename,
            'message': 'File uploaded successfully'
        }), 200

    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500


@upload_bp.route('/status/<file_id>', methods=['GET'])
def check_upload_status(file_id):
    """
    Check if uploaded file exists and is ready for processing.

    Returns:
    {
        "success": true,
        "file_id": "file-identifier",
        "exists": true,
        "ready_for_processing": true
    }
    """
    try:
        # Find file with this ID
        upload_folder = current_app.config['UPLOAD_FOLDER']
        files = [f for f in os.listdir(upload_folder) if f.startswith(file_id)]

        if not files:
            return jsonify({
                'success': True,
                'file_id': file_id,
                'exists': False,
                'ready_for_processing': False
            }), 200

        filename = files[0]
        filepath = os.path.join(upload_folder, filename)
        file_size = os.path.getsize(filepath)

        return jsonify({
            'success': True,
            'file_id': file_id,
            'exists': True,
            'ready_for_processing': file_size > 0,
            'file_size': file_size
        }), 200

    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500