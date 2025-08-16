from flask import Blueprint, request, jsonify
from app.models import db, Category
from app.utils.validators import validate_category_data

categories_bp = Blueprint('categories', __name__)


@categories_bp.route('/', methods=['POST'])
def create_category():
    data = request.get_json()
    is_valid, message = validate_category_data(data)
    if not is_valid:
        return jsonify({'error': message}), 400

    new_category = Category(
        subject_code=data['subject_code'],
        description=data.get('description')
    )
    db.session.add(new_category)
    db.session.commit()
    return jsonify({'id': new_category.id, 'subject_code': new_category.subject_code}), 201


@categories_bp.route('/', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'subject_code': c.subject_code,
        'description': c.description
    } for c in categories])
