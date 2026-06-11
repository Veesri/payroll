import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt
from werkzeug.security import generate_password_hash
from models import db, Employee, User, Department, SalaryStructure

employee_bp = Blueprint('employee', __name__)

def role_required(roles):
    def wrapper(fn):
        def decorator(*args, **kwargs):
            claims = get_jwt()
            if claims.get('role') not in roles:
                return jsonify(message="Unauthorized access!"), 403
            return fn(*args, **kwargs)
        decorator.__name__ = fn.__name__
        return decorator
    return wrapper

@employee_bp.route('/', methods=['GET'])
@jwt_required()
def get_employees():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    department_id = request.args.get('department_id')

    query = Employee.query
    
    if search:
        query = query.filter(db.or_(
            Employee.first_name.ilike(f'%{search}%'),
            Employee.last_name.ilike(f'%{search}%'),
            Employee.email.ilike(f'%{search}%')
        ))
    if department_id:
        query = query.filter(Employee.department_id == department_id)
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    employees = pagination.items

    return jsonify({
        'employees': [{
            'id': e.id,
            'first_name': e.first_name,
            'last_name': e.last_name,
            'email': e.email,
            'department_id': e.department_id,
            'department': e.department.name if e.department else None,
            'designation': e.designation,
            'status': e.status,
            'photo_url': e.photo_url
        } for e in employees],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@employee_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_employee(id):
    e = Employee.query.get_or_404(id)
    return jsonify({
        'id': e.id,
        'first_name': e.first_name,
        'last_name': e.last_name,
        'email': e.email,
        'phone': e.phone,
        'department_id': e.department_id,
        'department': e.department.name if e.department else None,
        'designation': e.designation,
        'status': e.status,
        'photo_url': e.photo_url,
        'basic_salary': e.salary_structure.basic_salary if e.salary_structure else 0
    }), 200

@employee_bp.route('/', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def add_employee():
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    
    # Check if user email/username exists
    if User.query.filter_by(username=data['username']).first() or Employee.query.filter_by(email=data['email']).first():
         return jsonify(message="User or Email already exists"), 400

    new_user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='employee'
    )
    db.session.add(new_user)
    db.session.flush()

    new_employee = Employee(
        user_id=new_user.id,
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        department_id=data.get('department_id') if data.get('department_id') else None,
        designation=data.get('designation'),
        phone=data.get('phone')
    )
    db.session.add(new_employee)
    db.session.flush()

    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            filename = secure_filename(f"emp_{new_employee.id}_{file.filename}")
            filepath = os.path.join(current_app.static_folder, filename)
            os.makedirs(current_app.static_folder, exist_ok=True)
            file.save(filepath)
            new_employee.photo_url = f"/uploads/{filename}"

    # Add default salary structure
    if 'basic_salary' in data and data['basic_salary']:
        salary = SalaryStructure(employee_id=new_employee.id, basic_salary=float(data['basic_salary']))
        db.session.add(salary)

    db.session.commit()
    return jsonify(message="Employee added successfully", id=new_employee.id), 201

@employee_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def update_employee(id):
    emp = Employee.query.get_or_404(id)
    
    # Handle form data for file uploads or json
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    emp.first_name = data.get('first_name', emp.first_name)
    emp.last_name = data.get('last_name', emp.last_name)
    emp.email = data.get('email', emp.email)
    emp.phone = data.get('phone', emp.phone)
    emp.department_id = data.get('department_id', emp.department_id)
    emp.designation = data.get('designation', emp.designation)
    emp.status = data.get('status', emp.status)

    if 'photo' in request.files:
        file = request.files['photo']
        if file.filename != '':
            filename = secure_filename(f"emp_{id}_{file.filename}")
            filepath = os.path.join(current_app.static_folder, filename)
            file.save(filepath)
            emp.photo_url = f"/uploads/{filename}"

    if 'basic_salary' in data:
        if emp.salary_structure:
            emp.salary_structure.basic_salary = float(data['basic_salary'])
        else:
            salary = SalaryStructure(employee_id=emp.id, basic_salary=float(data['basic_salary']))
            db.session.add(salary)

    db.session.commit()
    return jsonify(message="Employee updated successfully"), 200

@employee_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def delete_employee(id):
    emp = Employee.query.get_or_404(id)
    user = User.query.get(emp.user_id)
    db.session.delete(emp)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify(message="Employee deleted successfully"), 200

@employee_bp.route('/export/excel', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def export_excel():
    from utils.excel import generate_excel_report
    from flask import send_file
    
    employees = Employee.query.order_by(Employee.first_name).all()
    
    headers = ["EMP ID", "Full Name", "Email", "Phone", "Department", "Designation", "Status", "Joined Date"]
    data = []
    
    for emp in employees:
        data.append([
            f"EMP-{emp.id:04d}",
            f"{emp.first_name} {emp.last_name}",
            emp.email,
            emp.phone or "-",
            emp.department.name if emp.department else "N/A",
            emp.designation or "-",
            emp.status.capitalize(),
            emp.created_at.strftime('%Y-%m-%d')
        ])
        
    excel_file = generate_excel_report("Employee Directory Report", headers, data)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Employee_Report.xlsx'
    )
