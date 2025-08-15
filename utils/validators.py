import os
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def validate_image_file(file):
    """Validate uploaded image file."""
    if not file:
        return False, "No file provided"

    if file.filename == '':
        return False, "No file selected"

    if not allowed_file(file.filename):
        return False, "File type not allowed"

    return True, "Valid file"


def validate_evaluation_data(data):
    """Validate evaluation request data."""
    required_fields = ['teacher_answers', 'total_test_marks']

    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    if not isinstance(data['teacher_answers'], list):
        return False, "teacher_answers must be a list"

    if not isinstance(data['total_test_marks'], (int, float)):
        return False, "total_test_marks must be a number"

    for idx, answer in enumerate(data['teacher_answers']):
        if not all(key in answer for key in ['question_text', 'answer_text', 'marks_allotted']):
            return False, f"Invalid teacher answer format at index {idx}"

    return True, "Valid data"