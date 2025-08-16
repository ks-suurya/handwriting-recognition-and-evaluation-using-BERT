import os
import uuid
from flask import Blueprint, request, jsonify
from app.models import db, Submission, SubmissionImage, Student, ModelAnswer, Category
from app.services.s3_service import upload_file_to_s3, download_file_from_s3
from app.tasks import process_submission
from werkzeug.utils import secure_filename

submissions_bp = Blueprint('submissions', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@submissions_bp.route('/', methods=['POST'])
def create_submission():
    """
    Creates a new submission, uploads images to S3, and queues it for processing.
    Expects a multipart/form-data request with:
    - student_id
    - model_answer_id
    - files (multiple image files)
    """
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400

    files = request.files.getlist('files')
    student_id = request.form.get('student_id')
    model_answer_id = request.form.get('model_answer_id')

    if not all([student_id, model_answer_id, files]):
        return jsonify({'error': 'Missing student_id, model_answer_id, or files'}), 400

    # Create submission record
    new_submission = Submission(student_id=student_id, model_answer_id=model_answer_id)
    db.session.add(new_submission)
    db.session.commit()

    # Upload images to S3 and create image records
    for i, file in enumerate(files):
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}-{filename}"
            s3_key = f"student-submissions/{new_submission.id}/{unique_filename}"

            upload_file_to_s3(file, s3_key)

            image_record = SubmissionImage(
                submission_id=new_submission.id,
                s3_key=s3_key,
                page_order=i
            )
            db.session.add(image_record)
        else:
            return jsonify({'error': f'Invalid file type: {file.filename}'}), 400

    db.session.commit()

    # Queue the background task
    process_submission.delay(new_submission.id)

    return jsonify({
        'message': 'Submission received and is being processed.',
        'submission_id': new_submission.id
    }), 202


@submissions_bp.route('/<int:submission_id>', methods=['GET'])
def get_submission_status(submission_id):
    """
    Gets the status and result of a submission.
    """
    submission = Submission.query.get_or_404(submission_id)
    response = {
        'submission_id': submission.id,
        'status': submission.status,
        'final_score': submission.final_score,
        'submission_date': submission.submission_date.isoformat()
    }
    if submission.status == 'COMPLETED' and submission.result_s3_key:
        # Optionally, you could generate a pre-signed URL for the result file
        response['result_s3_key'] = submission.result_s3_key

    return jsonify(response), 200
