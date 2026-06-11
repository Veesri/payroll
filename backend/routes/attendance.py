from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Attendance, Employee, User
from datetime import datetime, date
from routes.employee import role_required

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/checkin', methods=['POST'])
@jwt_required()
def check_in():
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(user_id=user_id).first()
    if not employee:
        return jsonify({'message': 'Employee record not found'}), 404

    today = date.today()
    existing_attendance = Attendance.query.filter_by(employee_id=employee.id, attendance_date=today).first()

    if existing_attendance and existing_attendance.check_in:
        return jsonify({'message': 'Already checked in today'}), 400

    now = datetime.now()
    data = request.get_json() or {}
    
    if not existing_attendance:
        attendance = Attendance(
            employee_id=employee.id,
            attendance_date=today,
            check_in=now.time(),
            status='present',
            attendance_source=data.get('source', 'web')
        )
        db.session.add(attendance)
    else:
        existing_attendance.check_in = now.time()
        existing_attendance.status = 'present'
        existing_attendance.attendance_source = data.get('source', 'web')

    db.session.commit()
    return jsonify({'message': 'Check-in successful', 'time': now.strftime("%I:%M %p")}), 200

@attendance_bp.route('/export/excel', methods=['GET'])
@jwt_required()
def export_excel():
    from utils.excel import generate_excel_report
    from flask import send_file
    
    date_str = request.args.get('date')
    query = Attendance.query
    
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter_by(attendance_date=filter_date)
        except ValueError:
            pass
            
    attendances = query.all()
    
    headers = ["Employee ID", "Employee Name", "Department", "Attendance Date", "Check In", "Check Out", "Working Hours", "Status"]
    data = []
    
    for a in attendances:
        data.append([
            f"EMP-{a.employee.id:04d}",
            f"{a.employee.first_name} {a.employee.last_name}",
            a.employee.department.name if a.employee.department else "N/A",
            a.attendance_date.strftime('%Y-%m-%d'),
            a.check_in.strftime('%H:%M:%S') if a.check_in else "-",
            a.check_out.strftime('%H:%M:%S') if a.check_out else "-",
            f"{a.working_hours:.1f}" if a.working_hours else "0",
            a.status.capitalize() if a.status else "-"
        ])
        
    excel_file = generate_excel_report("Company Attendance Report", headers, data)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Attendance_Report.xlsx'
    )

@attendance_bp.route('/checkout', methods=['POST'])
@jwt_required()
def check_out():
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(user_id=user_id).first()
    if not employee:
        return jsonify({'message': 'Employee record not found'}), 404
        
    today = date.today()
    attendance = Attendance.query.filter_by(employee_id=employee.id, attendance_date=today).first()

    if not attendance or not attendance.check_in:
        return jsonify({'message': 'No check-in found for today. Please check-in first.'}), 400

    if attendance.check_out:
        return jsonify({'message': 'Already checked out today'}), 400

    now = datetime.now()
    attendance.check_out = now.time()

    # Calculate working hours
    check_in_dt = datetime.combine(today, attendance.check_in)
    check_out_dt = datetime.combine(today, attendance.check_out)
    duration = check_out_dt - check_in_dt
    attendance.working_hours = round(duration.total_seconds() / 3600, 2)

    db.session.commit()
    return jsonify({'message': 'Check-out successful', 'working_hours': attendance.working_hours, 'time': now.strftime("%I:%M %p")}), 200

@attendance_bp.route('/', methods=['GET'])
@jwt_required()
def get_attendance():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    employee_id_filter = request.args.get('employee_id', type=int)
    
    query = Attendance.query

    if user.role == 'employee':
        employee = Employee.query.filter_by(user_id=user_id).first()
        query = query.filter_by(employee_id=employee.id)
    else:
        if employee_id_filter:
            query = query.filter_by(employee_id=employee_id_filter)

    query = query.order_by(Attendance.attendance_date.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    records = []
    for a in pagination.items:
        emp = Employee.query.get(a.employee_id)
        records.append({
            'id': a.id,
            'employee_name': f"{emp.first_name} {emp.last_name}",
            'department': emp.department.name if emp.department else None,
            'date': a.attendance_date.strftime('%Y-%m-%d'),
            'check_in': a.check_in.strftime('%I:%M %p') if a.check_in else '-',
            'check_out': a.check_out.strftime('%I:%M %p') if a.check_out else '-',
            'working_hours': a.working_hours or 0,
            'status': a.status,
            'source': a.attendance_source
        })

    return jsonify({
        'attendance': records,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200

@attendance_bp.route('/report', methods=['GET'])
@jwt_required()
def get_report():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if user.role == 'employee':
        return jsonify({'message': 'Unauthorized'}), 403

    today = date.today()
    attendances_today = Attendance.query.filter_by(attendance_date=today).all()
    
    present = len([a for a in attendances_today if a.status == 'present'])
    # This is a basic calculation, in a real app you'd compare against total active employees
    total_employees = Employee.query.filter_by(status='active').count()
    absent = total_employees - present

    return jsonify({
        'present_today': present,
        'absent_today': absent,
        'total_employees': total_employees
    }), 200
