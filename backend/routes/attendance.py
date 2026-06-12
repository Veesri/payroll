from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Attendance, Employee, User, AttendanceQR, AttendanceLog, GPSSettings, AttendanceRule
from datetime import datetime, date, timedelta
from routes.employee import role_required
from sqlalchemy.orm import joinedload
import uuid
import jwt
import base64
import hashlib
from cryptography.fernet import Fernet
import math
import os

def get_cipher():
    secret = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
    fernet_key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(fernet_key)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi_1 = math.radians(lat1)
    phi_2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi_1) * math.cos(phi_2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

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
    
    query = Attendance.query.options(
        joinedload(Attendance.employee).joinedload(Employee.department)
    )

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
        emp = a.employee
        if emp:
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

@attendance_bp.route('/qr/generate', methods=['POST'])
@jwt_required()
@role_required(['super_admin', 'hr_admin'])
def generate_qr():
    # Invalidate existing active QRs
    active_qrs = AttendanceQR.query.filter_by(status='active').all()
    for aqr in active_qrs:
        aqr.status = 'closed'
    
    # Expiry options can be requested, default 1 min
    data = request.get_json() or {}
    expiry_minutes = int(data.get('expiry_minutes', 1))
    
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=expiry_minutes)
    
    session_id = f"ATT{now.strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:4].upper()}"
    
    secret = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
    payload = {
        "session_id": session_id,
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat()
    }
    jwt_token = jwt.encode(payload, secret, algorithm="HS256")
    
    cipher = get_cipher()
    encrypted_token = cipher.encrypt(jwt_token.encode()).decode()
    
    qr_record = AttendanceQR(
        session_id=session_id,
        token=encrypted_token,
        generated_at=now,
        expires_at=expires_at,
        status='active'
    )
    db.session.add(qr_record)
    
    log = AttendanceLog(
        employee_id=User.query.get(get_jwt_identity()).employee.id if User.query.get(get_jwt_identity()).employee else 1,
        action="qr_generate"
    )
    db.session.add(log)
    
    db.session.commit()
    
    return jsonify({
        "message": "QR Generated Successfully",
        "qr_data": {
            "session_id": session_id,
            "token": encrypted_token,
            "generated_at": now.isoformat(),
            "expires_at": expires_at.isoformat()
        }
    }), 201

@attendance_bp.route('/qr/active', methods=['GET'])
@jwt_required()
@role_required(['super_admin', 'hr_admin'])
def get_active_qr():
    qr = AttendanceQR.query.filter_by(status='active').first()
    if not qr:
        return jsonify({"message": "No active QR found"}), 404
    
    if datetime.utcnow() > qr.expires_at:
        qr.status = 'expired'
        db.session.commit()
        return jsonify({"message": "Active QR has expired"}), 404
        
    return jsonify({
        "qr_data": {
            "session_id": qr.session_id,
            "token": qr.token,
            "generated_at": qr.generated_at.isoformat(),
            "expires_at": qr.expires_at.isoformat()
        }
    }), 200

@attendance_bp.route('/qr/scan', methods=['POST'])
@jwt_required()
def scan_qr():
    user_id = get_jwt_identity()
    employee = Employee.query.filter_by(user_id=user_id).first()
    if not employee:
        return jsonify({'message': 'Employee record not found'}), 404
        
    data = request.get_json() or {}
    token = data.get('token')
    lat = data.get('latitude')
    lng = data.get('longitude')
    device = request.user_agent.string
    ip = request.remote_addr
    
    def create_log(action_str):
        log = AttendanceLog(
            employee_id=employee.id,
            action=action_str,
            latitude=lat,
            longitude=lng,
            device=device,
            ip_address=ip
        )
        db.session.add(log)
        db.session.commit()
    
    if not token:
        create_log("scan_rejected_missing_token")
        return jsonify({'message': 'QR token is missing'}), 400
        
    # Decrypt and Verify
    cipher = get_cipher()
    secret = os.environ.get('JWT_SECRET_KEY', 'super-secret-jwt-key')
    
    try:
        decrypted_jwt = cipher.decrypt(token.encode()).decode()
        payload = jwt.decode(decrypted_jwt, secret, algorithms=["HS256"])
    except Exception as e:
        create_log("scan_rejected_tampered")
        return jsonify({'message': 'Invalid or Tampered QR Token'}), 400
        
    session_id = payload.get("session_id")
    
    qr_record = AttendanceQR.query.filter_by(session_id=session_id).first()
    if not qr_record:
        create_log("scan_rejected_invalid_session")
        return jsonify({'message': 'QR Session not found'}), 404
        
    if qr_record.status != 'active' or datetime.utcnow() > qr_record.expires_at:
        if qr_record.status == 'active':
            qr_record.status = 'expired'
            db.session.commit()
        create_log("scan_rejected_expired")
        return jsonify({'message': 'QR Code has expired'}), 400

    # GPS Validation
    if lat is None or lng is None:
        create_log("scan_rejected_no_gps")
        return jsonify({'message': 'GPS Location is required'}), 400
        
    gps_setting = GPSSettings.query.first()
    if gps_setting:
        distance = haversine(float(lat), float(lng), gps_setting.latitude, gps_setting.longitude)
        if distance > gps_setting.radius:
            create_log("scan_rejected_outside_radius")
            return jsonify({'message': 'You are outside office premises.'}), 400
            
    # Business Logic (Check-in / Check-out)
    now = datetime.now()
    today = date.today()
    existing_attendance = Attendance.query.filter_by(employee_id=employee.id, attendance_date=today).first()
    
    rules = AttendanceRule.query.first()
    
    if not existing_attendance or not existing_attendance.check_in:
        # Check-in flow
        status = 'present'
        if rules and rules.office_start_time:
            # check late
            grace_dt = datetime.combine(today, rules.office_start_time) + timedelta(minutes=rules.grace_minutes)
            if now > grace_dt:
                status = 'late'
                
        if not existing_attendance:
            attendance = Attendance(
                employee_id=employee.id,
                attendance_date=today,
                check_in=now.time(),
                status=status,
                attendance_source='qr',
                latitude=lat,
                longitude=lng,
                ip_address=ip,
                device_details=device,
                qr_session_id=session_id
            )
            db.session.add(attendance)
        else:
            existing_attendance.check_in = now.time()
            existing_attendance.status = status
            existing_attendance.attendance_source = 'qr'
            existing_attendance.qr_session_id = session_id
        
        create_log("check_in_success")
        return jsonify({'message': 'Check-in successful', 'time': now.strftime("%I:%M %p")}), 200
    
    else:
        # Check-out flow
        if existing_attendance.check_out:
            create_log("scan_rejected_duplicate")
            return jsonify({'message': 'Attendance already marked.'}), 400
            
        existing_attendance.check_out = now.time()
        
        check_in_dt = datetime.combine(today, existing_attendance.check_in)
        check_out_dt = datetime.combine(today, existing_attendance.check_out)
        duration = check_out_dt - check_in_dt
        working_hours = round(duration.total_seconds() / 3600, 2)
        existing_attendance.working_hours = working_hours
        
        if rules:
            if working_hours < rules.half_day_hours:
                existing_attendance.status = 'half_day'
            if working_hours > rules.overtime_hours:
                # Add logic for overtime if needed or adjust status
                pass
                
        create_log("check_out_success")
        return jsonify({'message': 'Check-out successful', 'working_hours': working_hours, 'time': now.strftime("%I:%M %p")}), 200
