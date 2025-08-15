from flask import Blueprint, request, jsonify
from app.services.bert_service import BERTService
from app.utils.validators import validate_evaluation_data
import json
import os
from flask import current_app
import logging

logger = logging.getLogger(__name__)

evaluation_bp = Blueprint('evaluation', __name__)
bert_service = BERTService()


@evaluation_bp.route('/evaluate', methods=['POST'])
def evaluate_answers():
    """
    Evaluate student answers against teacher reference answers.

    Expected JSON:
    {
        "file_id": "student-answers-file-id",
        "teacher_answers": [
            {
                "question_text": "What is photosynthesis?",
                "answer_text": "Process by which plants make food using sunlight",
                "marks_allotted": 5
            }
        ],
        "total_test_marks": 20
    }

    Returns:
    {
        "success": true,
        "evaluation_id": "unique-evaluation-id",
        "summary": {
            "total_obtained_marks": 18.5,
            "total_marks_allotted": 20,
            "total_test_marks": 20,
            "final_score": 18,
            "processing_time": 2.3
        },
        "results": [
            {
                "question_id": "Q1",
                "question_text": "What is photosynthesis?",
                "student_answer": "Student's answer text",
                "teacher_answer": "Reference answer text",
                "similarity_score": 85.5,
                "length_score": 0.9,
                "marks_allotted": 5,
                "question_score": 3.8
            }
        ]
    }
    """
    try:
        data = request.get_json()

        # Validate request data
        is_valid, message = validate_evaluation_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'error': message
            }), 400

        # Get student answers from OCR results
        file_id = data.get('file_id')
        if not file_id:
            return jsonify({
                'success': False,
                'error': 'file_id is required'
            }), 400

        # Load student answers
        results_folder = current_app.config['RESULTS_FOLDER']
        result_filename = f"{file_id}_ocr_results.json"
        result_path = os.path.join(results_folder, result_filename)

        if not os.path.exists(result_path):
            return jsonify({
                'success': False,
                'error': 'Student answers not found. Please process the image first.'
            }), 404

        with open(result_path, 'r') as f:
            ocr_results = json.load(f)

        if not ocr_results['success']:
            return jsonify({
                'success': False,
                'error': 'OCR processing was not successful'
            }), 400

        student_answers = ocr_results['questions']
        teacher_answers = data['teacher_answers']
        total_test_marks = data['total_test_marks']

        # Perform evaluation
        evaluation_summary = bert_service.evaluate_answers(
            teacher_answers, student_answers, total_test_marks
        )

        # Generate evaluation ID
        import uuid
        evaluation_id = str(uuid.uuid4())

        # Save evaluation results
        evaluation_result = {
            'evaluation_id': evaluation_id,
            'file_id': file_id,
            'summary': {
                'total_obtained_marks': evaluation_summary.total_obtained_marks,
                'total_marks_allotted': evaluation_summary.total_marks_allotted,
                'total_test_marks': evaluation_summary.total_test_marks,
                'final_score': evaluation_summary.final_score,
                'processing_time': evaluation_summary.processing_time
            },
            'results': []
        }

        # Convert results to dict format
        for result in evaluation_summary.results_per_question:
            evaluation_result['results'].append({
                'question_id': result.question_id,
                'question_text': result.question_text,
                'student_answer': result.student_answer,
                'teacher_answer': result.teacher_answer,
                'similarity_score': result.similarity_score,
                'length_score': result.length_score,
                'marks_allotted': result.marks_allotted,
                'question_score': result.question_score
            })

        # Save evaluation results
        eval_filename = f"{evaluation_id}_evaluation.json"
        eval_path = os.path.join(results_folder, eval_filename)
        with open(eval_path, 'w') as f:
            json.dump(evaluation_result, f, indent=2)

        logger.info(f"Evaluation completed: {evaluation_id}")

        return jsonify({
            'success': True,
            **evaluation_result
        }), 200

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Evaluation failed'
        }), 500


@evaluation_bp.route('/results/<evaluation_id>', methods=['GET'])
def get_evaluation_results(evaluation_id):
    """
    Get previously completed evaluation results.

    Returns: Same format as evaluate_answers endpoint
    """
    try:
        results_folder = current_app.config['RESULTS_FOLDER']
        eval_filename = f"{evaluation_id}_evaluation.json"
        eval_path = os.path.join(results_folder, eval_filename)

        if not os.path.exists(eval_path):
            return jsonify({
                'success': False,
                'error': 'Evaluation results not found'
            }), 404

        with open(eval_path, 'r') as f:
            results = json.load(f)

        return jsonify({
            'success': True,
            **results
        }), 200

    except Exception as e:
        logger.error(f"Failed to retrieve evaluation results: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve evaluation results'
        }), 500


@evaluation_bp.route('/summary/<evaluation_id>', methods=['GET'])
def get_evaluation_summary(evaluation_id):
    """
    Get evaluation summary without detailed question results.

    Returns:
    {
        "success": true,
        "evaluation_id": "evaluation-id",
        "summary": {
            "total_obtained_marks": 18.5,
            "total_marks_allotted": 20,
            "total_test_marks": 20,
            "final_score": 18,
            "processing_time": 2.3
        }
    }
    """
    try:
        results_folder = current_app.config['RESULTS_FOLDER']
        eval_filename = f"{evaluation_id}_evaluation.json"
        eval_path = os.path.join(results_folder, eval_filename)

        if not os.path.exists(eval_path):
            return jsonify({
                'success': False,
                'error': 'Evaluation results not found'
            }), 404

        with open(eval_path, 'r') as f:
            results = json.load(f)

        return jsonify({
            'success': True,
            'evaluation_id': results['evaluation_id'],
            'summary': results['summary']
        }), 200

    except Exception as e:
        logger.error(f"Failed to retrieve evaluation summary: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve evaluation summary'
        }), 500