from flask import Blueprint, request, jsonify
from app.models import db, Student
from app.utils.validators import validate_student_data

students_bp = Blueprint('students', __name__)


@students_bp.route('/', methods=['POST'])
def create_student():
    data = request.get_json()
    is_valid, message = validate_student_data(data)
    if not is_valid:
        return jsonify({'error': message}), 400

    new_student = Student(name=data['name'], email=data.get('email'))
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'id': new_student.id, 'name': new_student.name}), 201


@students_bp.route('/', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{'id': s.id, 'name': s.name, 'email': s.email} for s in students])
