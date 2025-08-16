ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_student_data(data):
    if not data or 'name' not in data:
        return False, 'Missing student name'
    return True, ''


def validate_category_data(data):
    if not data or 'subject_code' not in data:
        return False, 'Missing subject code'
    return True, ''


def validate_model_answer_data(data):
    if not data:
        return False, 'Missing data'
    if 'name' not in data or 'category_id' not in data:
        return False, 'Missing name or category_id'
    if 'answers' not in data or not isinstance(data['answers'], list):
        return False, 'Missing or invalid answers list'
    if 'total_test_marks' not in data:
        return False, 'Missing total_test_marks'

    for answer in data['answers']:
        if not all(k in answer for k in ['question_id', 'answer_text', 'marks_allotted']):
            return False, 'Each answer must have question_id, answer_text, and marks_allotted'

    return True, ''
