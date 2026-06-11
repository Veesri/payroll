from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, User, Employee

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role') # User should select role to login, or we infer it.

    if not username or not password:
        return jsonify({'message': 'Username and password are required'}), 400

    user = User.query.filter_by(username=username).first()

    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    if role and user.role != role:
        return jsonify({'message': 'Unauthorized role access'}), 403

    if not user.is_approved:
        return jsonify({'message': 'Account is pending admin approval'}), 403

    if not user.is_active:
        return jsonify({'message': 'Account is inactive'}), 403

    access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role, 'username': user.username})
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    role = data.get('role')  # 'hr_admin' or 'employee'

    if not username or not password or not email or not first_name or not last_name or not role:
        return jsonify({'message': 'All fields are required'}), 400

    if role not in ['hr_admin', 'employee']:
        return jsonify({'message': 'Invalid role specified'}), 400

    # Check if username or email already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username is already taken'}), 400

    if Employee.query.filter_by(email=email).first():
        return jsonify({'message': 'Email is already registered'}), 400

    try:
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role=role,
            is_active=True,
            is_approved=False
        )
        db.session.add(new_user)
        db.session.flush()

        new_employee = Employee(
            user_id=new_user.id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            status='inactive'  # pending approval
        )
        db.session.add(new_employee)
        db.session.commit()

        return jsonify({'message': 'Registration successful! Pending admin approval.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    claims = get_jwt()
    if claims.get('role') != 'super_admin':
        return jsonify({'message': 'Super admin access required'}), 403

    users = User.query.filter(User.role != 'super_admin').all()
    user_list = []
    for u in users:
        emp = u.employee
        user_list.append({
            'id': u.id,
            'username': u.username,
            'role': u.role,
            'is_approved': u.is_approved,
            'is_active': u.is_active,
            'created_at': u.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'first_name': emp.first_name if emp else '',
            'last_name': emp.last_name if emp else '',
            'email': emp.email if emp else ''
        })
    return jsonify(user_list), 200

@auth_bp.route('/users/<int:user_id>/approve', methods=['POST'])
@jwt_required()
def approve_user(user_id):
    claims = get_jwt()
    if claims.get('role') != 'super_admin':
        return jsonify({'message': 'Super admin access required'}), 403

    user = User.query.get_or_404(user_id)
    user.is_approved = True
    if user.employee:
        user.employee.status = 'active'
    db.session.commit()
    return jsonify({'message': f'User {user.username} approved successfully'}), 200

@auth_bp.route('/users/<int:user_id>/toggle-active', methods=['POST'])
@jwt_required()
def toggle_active(user_id):
    claims = get_jwt()
    if claims.get('role') != 'super_admin':
        return jsonify({'message': 'Super admin access required'}), 403

    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({
        'message': f'User active status toggled successfully',
        'is_active': user.is_active
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404
        
    employee_data = None
    if user.employee:
        employee_data = {
            'id': user.employee.id,
            'first_name': user.employee.first_name,
            'last_name': user.employee.last_name,
            'department_id': user.employee.department_id,
            'designation': user.employee.designation,
        }

    return jsonify({
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'employee': employee_data
    }), 200

