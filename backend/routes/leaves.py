from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Leave, LeaveType, Employee, User
from datetime import datetime
from routes.employee import role_required

leave_bp = Blueprint('leave', __name__)

@leave_bp.route('/types', methods=['GET'])
@jwt_required()
def get_leave_types():
    types = LeaveType.query.all()
    return jsonify([{'id': t.id, 'name': t.name, 'days_allowed': t.days_allowed} for t in types]), 200

@leave_bp.route('/', methods=['POST'])
@jwt_required()
def apply_leave():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    employee = Employee.query.filter_by(user_id=user_id).first()
    
    if not employee:
        if user.role in ['hr_admin', 'super_admin']:
            # Auto-create a stub employee record so Admins can use the leave system
            employee = Employee(
                user_id=user.id,
                first_name=user.username,
                last_name='(Admin)',
                email=f"{user.username}@system.local"
            )
            db.session.add(employee)
            db.session.flush() # Get the new ID without committing yet
        else:
            return jsonify({'message': 'Employee record not found'}), 404

    data = request.get_json()
    from_date = datetime.strptime(data['from_date'], '%Y-%m-%d').date()
    to_date = datetime.strptime(data['to_date'], '%Y-%m-%d').date()
    
    user = User.query.get(user_id)
    
    # Set approval routing based on requester's role
    if user.role == 'employee':
        req_role = 'employee'
        appr_level = 'hr_admin'
    elif user.role == 'hr_admin':
        req_role = 'hr_admin'
        appr_level = 'super_admin'
    else:
        req_role = user.role
        appr_level = 'super_admin' # Fallback
        
    leave = Leave(
        employee_id=employee.id,
        leave_type_id=data['leave_type_id'],
        from_date=from_date,
        to_date=to_date,
        reason=data.get('reason'),
        status='pending',
        requested_by_role=req_role,
        approval_level=appr_level
    )
    db.session.add(leave)
    db.session.commit()
    return jsonify({'message': 'Leave application submitted successfully'}), 201

@leave_bp.route('/', methods=['GET'])
@jwt_required()
def get_leaves():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    query = Leave.query

    personal = request.args.get('personal') == 'true'
    
    if user.role == 'employee':
        employee = Employee.query.filter_by(user_id=user_id).first()
        if employee:
            query = query.filter_by(employee_id=employee.id)
        else:
            query = query.filter(False) # Return empty list if no employee record
    elif user.role == 'hr_admin':
        if personal:
            employee = Employee.query.filter_by(user_id=user_id).first()
            if employee:
                query = query.filter_by(employee_id=employee.id)
            else:
                query = query.filter(False)
        else:
            query = query.filter_by(approval_level='hr_admin')
    elif user.role == 'super_admin':
        if personal:
            employee = Employee.query.filter_by(user_id=user_id).first()
            if employee:
                query = query.filter_by(employee_id=employee.id)
            else:
                query = query.filter(False)
        else:
            query = query.filter_by(approval_level='super_admin')

    query = query.order_by(Leave.applied_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    records = []
    for l in pagination.items:
        emp = Employee.query.get(l.employee_id)
        l_type = LeaveType.query.get(l.leave_type_id)
        records.append({
            'id': l.id,
            'employee_name': f"{emp.first_name} {emp.last_name}",
            'leave_type': l_type.name,
            'from_date': l.from_date.strftime('%Y-%m-%d'),
            'to_date': l.to_date.strftime('%Y-%m-%d'),
            'status': l.status,
            'reason': l.reason,
            'comments': l.comments,
            'applied_at': l.applied_at.strftime('%Y-%m-%d') if l.applied_at else None
        })

    return jsonify({
        'leaves': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@leave_bp.route('/<int:id>/approve', methods=['PUT'])
@jwt_required()
def approve_leave(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role == 'employee':
        return jsonify({'message': 'Unauthorized'}), 403

    leave = Leave.query.get_or_404(id)
    
    # Check hierarchy
    if leave.approval_level != user.role and user.role != 'super_admin':
        return jsonify({'message': 'You do not have permission to approve this leave request level.'}), 403

    data = request.get_json() or {}
    
    leave.status = 'approved'
    leave.approved_by = user_id
    leave.approved_by_role = user.role
    leave.comments = data.get('comments', '')
    
    db.session.commit()
    return jsonify({'message': 'Leave approved successfully'}), 200

@leave_bp.route('/export/excel', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def export_excel():
    from utils.excel import generate_excel_report
    from flask import send_file
    
    status = request.args.get('status')
    query = Leave.query
    if status:
        query = query.filter_by(status=status)
        
    leaves = query.order_by(Leave.applied_at.desc()).all()
    
    headers = ["Leave ID", "Employee Name", "Department", "Leave Type", "From Date", "To Date", "Days", "Status", "Reason", "Applied On"]
    data = []
    
    for lv in leaves:
        days = (lv.to_date - lv.from_date).days + 1
        data.append([
            f"LV-{lv.id:04d}",
            f"{lv.employee.first_name} {lv.employee.last_name}",
            lv.employee.department.name if lv.employee.department else "N/A",
            lv.leave_type.name if lv.leave_type else "N/A",
            lv.from_date.strftime('%Y-%m-%d'),
            lv.to_date.strftime('%Y-%m-%d'),
            days,
            lv.status.capitalize(),
            lv.reason,
            lv.applied_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    excel_file = generate_excel_report("Employee Leave Report", headers, data)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Leave_Report.xlsx'
    )

@leave_bp.route('/<int:id>/reject', methods=['PUT'])
@jwt_required()
def reject_leave(id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role == 'employee':
        return jsonify({'message': 'Unauthorized'}), 403

    leave = Leave.query.get_or_404(id)
    
    # Check hierarchy
    if leave.approval_level != user.role and user.role != 'super_admin':
        return jsonify({'message': 'You do not have permission to reject this leave request level.'}), 403

    data = request.get_json() or {}
    
    leave.status = 'rejected'
    leave.approved_by = user_id
    leave.approved_by_role = user.role
    leave.comments = data.get('comments', '')
    
    db.session.commit()
    return jsonify({'message': 'Leave rejected successfully'}), 200
