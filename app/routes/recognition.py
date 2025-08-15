from flask import Blueprint, request, jsonify, current_app
import os
from app.services.ocr_service import OCRService
import logging

logger = logging.getLogger(__name__)

recognition_bp = Blueprint('recognition', __name__)
ocr_service = OCRService()


@recognition_bp.route('/process/<file_id>', methods=['POST'])
def process_image(file_id):
    """
    Process uploaded image for text recognition.

    Returns:
    {
        "success": true,
        "file_id": "file-identifier",
        "total_questions": 3,
        "questions": [
            {
                "question_id": "Q1",
                "recognized_text": "Original OCR text",
                "corrected_text": "AI corrected text",
                "region": {"top": 100, "bottom": 200},
                "word_count": 15,
                "confidence": 0.92
            }
        ],
        "processing_info": {
            "original_size": [1200, 800, 3],
            "text_regions_found": 3,
            "ai_correction_available": true
        }
    }
    """
    try:
        # Find uploaded file
        upload_folder = current_app.config['UPLOAD_FOLDER']
        files = [f for f in os.listdir(upload_folder) if f.startswith(file_id)]

        if not files:
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404

        filename = files[0]
        filepath = os.path.join(upload_folder, filename)

        # Process image
        result = ocr_service.process_image(filepath)

        if result['success']:
            # Save results for later use
            results_folder = current_app.config['RESULTS_FOLDER']
            result_filename = f"{file_id}_ocr_results.json"
            result_path = os.path.join(results_folder, result_filename)

            import json
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)

            logger.info(f"OCR processing completed: {file_id}")

            return jsonify({
                'success': True,
                'file_id': file_id,
                **result
            }), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        logger.error(f"OCR processing failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Processing failed'
        }), 500


@recognition_bp.route('/results/<file_id>', methods=['GET'])
def get_recognition_results(file_id):
    """
    Get previously processed recognition results.

    Returns: Same format as process_image endpoint
    """
    try:
        results_folder = current_app.config['RESULTS_FOLDER']
        result_filename = f"{file_id}_ocr_results.json"
        result_path = os.path.join(results_folder, result_filename)

        if not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404

        import json
        with open(result_path, 'r') as f:
            results = json.load(f)

        return jsonify({
            'success': True,
            'file_id': file_id,
            **results
        }), 200

    except Exception as e:
        logger.error(f"Failed to retrieve results: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve results'
        }), 500


@recognition_bp.route('/questions/<file_id>', methods=['GET'])
def get_extracted_questions(file_id):
    """
    Get only the extracted questions and answers in a clean format.

    Returns:
    {
        "success": true,
        "file_id": "file-identifier",
        "questions": [
            {
                "question_id": "Q1",
                "answer": "Final corrected answer text",
                "confidence": 0.92,
                "word_count": 15
            }
        ]
    }
    """
    try:
        results_folder = current_app.config['RESULTS_FOLDER']
        result_filename = f"{file_id}_ocr_results.json"
        result_path = os.path.join(results_folder, result_filename)

        if not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'Results not found'
            }), 404

        import json
        with open(result_path, 'r') as f:
            results = json.load(f)

        if not results['success']:
            return jsonify(results), 500

        # Extract clean question format
        questions = []
        for q in results['questions']:
            questions.append({
                'question_id': q['question_id'],
                'answer': q['corrected_text'],
                'confidence': q['confidence'],
                'word_count': q['word_count']
            })

        return jsonify({
            'success': True,
            'file_id': file_id,
            'questions': questions
        }), 200

    except Exception as e:
        logger.error(f"Failed to retrieve questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve questions'
        }), 500