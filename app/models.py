from app.extensions import db
from datetime import datetime

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True)
    submissions = db.relationship('Submission', backref='student', lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    model_answers = db.relationship('ModelAnswer', backref='category', lazy=True)

class ModelAnswer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    s3_key = db.Column(db.String(255), nullable=False) # Key to the JSON file in S3
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    model_answer_id = db.Column(db.Integer, db.ForeignKey('model_answer.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='PENDING') # PENDING, PROCESSING, COMPLETED, FAILED
    final_score = db.Column(db.Float, nullable=True)
    result_s3_key = db.Column(db.String(255), nullable=True) # Key to the result JSON in S3
    images = db.relationship('SubmissionImage', backref='submission', lazy=True, cascade="all, delete-orphan")

class SubmissionImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'), nullable=False)
    s3_key = db.Column(db.String(255), nullable=False) # Key to the image file in S3
    page_order = db.Column(db.Integer, nullable=False)
