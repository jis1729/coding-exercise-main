from flask import request, jsonify, Blueprint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from ..models import Student
from ..app import db
import re

student_bp = Blueprint('students', __name__)

# Health check route
@student_bp.route('/service/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})

# Create a student
@student_bp.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()
    if 'last_name' not in data:
        return jsonify('error: Missing required field: last_name'), 422
    if ('email' not in data or data.get('email') == '') and ('username' not in data or data.get('username') == ''):
        return jsonify('error: Missing required field: email/username'), 422
    if 'email' in data and data['email'] != '' and not is_valid_email(data['email']):
        return jsonify('error: Not a valid email'), 422
    try:
        new_student = Student(
        email=data.get('email') or data.get('username'),
        first_name=data.get('first_name'),
        last_name=data['last_name'],
        display_name=data.get('display_name') or f"{data['first_name']} {data['last_name']}".strip(),
        started_at=data.get('started_at')
        )
        db.session.add(new_student)
        db.session.commit()
        print(jsonify({
            'id': new_student.id,
            'email': new_student.email,
            'first_name': new_student.first_name,
            'last_name': new_student.last_name,
            'display_name': new_student.display_name,
            'created_at': new_student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'started_at': new_student.started_at.strftime('%Y-%m-%d')
        }))
        return jsonify({
            'id': new_student.id,
            'email': new_student.email,
            'first_name': new_student.first_name,
            'last_name': new_student.last_name,
            'display_name': new_student.display_name,
            'created_at': new_student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'started_at': new_student.started_at.strftime('%Y-%m-%d')
        }), 201
    except IntegrityError as e:
        return jsonify({'error': 'Integrity error occurred'}), 409
    except SQLAlchemyError as e:
        return jsonify({'error': 'Unprocessable Entity'}), 422

# Retrieve a particular student by ID
@student_bp.route('/students/<int:student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.get_or_404(student_id)
    return jsonify({
        'id': student.id,
        'email': student.email,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'display_name': student.display_name,
        'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'started_at': student.started_at.strftime('%Y-%m-%d')
    })

# Search students
@student_bp.route('/students', methods=['GET'])
def search_students():
    name = request.args.get('name')
    username = request.args.get('username')
    email = request.args.get('email')
    started_after = request.args.get('started_after')

    #Check if no search criteria provided
    if not any([name, username, email, started_after]):
        return jsonify('error: No search criteria provided.'), 400

    query = Student.query

    if name:
        query = query.filter(
            (Student.first_name.ilike(f'%{name}%')) | 
            (Student.last_name.ilike(f'%{name}%')) |
            (Student.display_name.ilike(f'%{name}%'))
        )
    
    if username:
        query = query.filter(Student.email.ilike(f'%{username}%'))
    
    if email:
        query = query.filter(Student.email.ilike(f'%{email}%'))
    
    if started_after:
        query = query.filter(Student.started_at >= started_after)
    
    students = query.all()

    return jsonify({
        'students': [{
            'id': student.id,
            'email': student.email,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'display_name': student.display_name,
            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'started_at': student.started_at.strftime('%Y-%m-%d')
        } for student in students]
    })

def is_valid_email(email):
    # Define a basic pattern for an email
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # Use regex to match the email pattern
    if re.match(pattern, email):
        return True
    else:
        return False