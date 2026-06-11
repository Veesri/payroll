from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import db, Department

department_bp = Blueprint('department', __name__)

# Super Admin only decorator logic
def role_required(role):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') != role:
                return jsonify(message="Admins only!"), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper

@department_bp.route('/', methods=['GET'])
@jwt_required()
def get_departments():
    departments = Department.query.all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'description': d.description,
        'head_id': d.head_id,
        'created_at': d.created_at
    } for d in departments]), 200

@department_bp.route('/', methods=['POST'])
@jwt_required()
@role_required('super_admin')
def create_department():
    data = request.get_json()
    new_dept = Department(name=data['name'], description=data.get('description'))
    db.session.add(new_dept)
    db.session.commit()
    return jsonify(message="Department created successfully", id=new_dept.id), 201

@department_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required('super_admin')
def update_department(id):
    dept = Department.query.get_or_404(id)
    data = request.get_json()
    dept.name = data.get('name', dept.name)
    dept.description = data.get('description', dept.description)
    dept.head_id = data.get('head_id', dept.head_id)
    db.session.commit()
    return jsonify(message="Department updated successfully"), 200

@department_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required('super_admin')
def delete_department(id):
    dept = Department.query.get_or_404(id)
    db.session.delete(dept)
    db.session.commit()
    return jsonify(message="Department deleted successfully"), 200
