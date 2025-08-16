import os
import json
from app import celery  # Import the celery instance from __init__
from app.extensions import db
from app.services.s3_service import download_file_from_s3, upload_file_to_s3
from app.services.ocr_service import OCRService
from app.services.bert_service import BERTService
from app.models import Submission, ModelAnswer


@celery.task(name='app.tasks.process_submission')
def process_submission(submission_id):
    """
    Celery task to process a submission in the background.
    The app context is automatically provided by the ContextTask class.
    """
    submission = Submission.query.get(submission_id)
    if not submission:
        print(f"Submission with id {submission_id} not found.")
        return

    submission.status = 'PROCESSING'
    db.session.commit()

    try:
        # 1. Download model answer JSON from S3
        model_answer_obj = ModelAnswer.query.get(submission.model_answer_id)
        model_answer_content = download_file_from_s3(model_answer_obj.s3_key)
        model_answer_data = json.loads(model_answer_content)
        teacher_answers = model_answer_data.get('answers', [])
        total_test_marks = model_answer_data.get('total_test_marks', 100)

        # 2. Process each image with OCR service
        ocr_service = OCRService()
        all_student_answers = []

        sorted_images = sorted(submission.images, key=lambda x: x.page_order)

        # Create a temporary directory for images if it doesn't exist
        temp_dir = '/tmp'
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        for image_record in sorted_images:
            image_content = download_file_from_s3(image_record.s3_key)

            temp_image_path = os.path.join(temp_dir, os.path.basename(image_record.s3_key))
            with open(temp_image_path, 'wb') as f:
                f.write(image_content)

            ocr_result = ocr_service.process_image(temp_image_path)
            os.remove(temp_image_path)

            if ocr_result.get('success'):
                all_student_answers.extend(ocr_result.get('questions', []))

        # 3. Evaluate with BERT service
        bert_service = BERTService()
        evaluation_summary = bert_service.evaluate_answers(
            teacher_answers, all_student_answers, total_test_marks
        )

        # 4. Prepare and upload final result JSON to S3
        final_result = evaluation_summary.to_dict()
        final_result['submission_id'] = submission.id
        final_result['student_id'] = submission.student_id

        result_json_content = json.dumps(final_result, indent=2)
        result_s3_key = f"evaluation-results/{submission.id}-result.json"
        upload_file_to_s3(result_json_content.encode('utf-8'), result_s3_key, content_type='application/json')

        # 5. Update submission record in DB
        submission.status = 'COMPLETED'
        submission.final_score = evaluation_summary.final_score
        submission.result_s3_key = result_s3_key
        db.session.commit()

    except Exception as e:
        submission.status = 'FAILED'
        db.session.commit()
        print(f"Error processing submission {submission_id}: {str(e)}")
        raise
