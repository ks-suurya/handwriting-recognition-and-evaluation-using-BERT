import json
import uuid
from flask import Blueprint, request, jsonify
from app.models import db, ModelAnswer
from app.services.s3_service import upload_file_to_s3
from app.utils.validators import validate_model_answer_data

model_answers_bp = Blueprint('model_answers', __name__)

@model_answers_bp.route('/', methods=['POST'])
def create_model_answer():
    data = request.get_json()
    is_valid, message = validate_model_answer_data(data)
    if not is_valid:
        return jsonify({'error': message}), 400

    # Upload the JSON content to S3
    json_content = json.dumps(data).encode('utf-8')
    s3_key = f"model-answers/{uuid.uuid4()}.json"
    upload_file_to_s3(json_content, s3_key, content_type='application/json')

    # Save metadata to the database
    new_answer = ModelAnswer(
        name=data['name'],
        category_id=data['category_id'],
        s3_key=s3_key
    )
    db.session.add(new_answer)
    db.session.commit()

    return jsonify({
        'id': new_answer.id,
        'name': new_answer.name,
        's3_key': new_answer.s3_key
    }), 201

@model_answers_bp.route('/', methods=['GET'])
def get_model_answers():
    answers = ModelAnswer.query.all()
    return jsonify([{
        'id': a.id,
        'name': a.name,
        'category_id': a.category_id,
        'created_at': a.created_at.isoformat()
    } for a in answers])
