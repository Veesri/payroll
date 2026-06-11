from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, Payroll, Employee, Attendance, Leave
from datetime import datetime
import calendar
from routes.employee import role_required

payroll_bp = Blueprint('payroll', __name__)

@payroll_bp.route('/generate', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def generate_payroll():
    data = request.get_json()
    month = data.get('month')
    year = data.get('year')
    employee_id = data.get('employee_id') # Optional: If provided, generates for single employee
    overtime_hours_map = data.get('overtime_hours', {}) # dict mapping emp_id -> hours
    
    if not month or not year:
        return jsonify(message="Month and year are required"), 400

    query = Employee.query.filter_by(status='active')
    if employee_id:
        query = query.filter_by(id=employee_id)
        
    employees = query.all()
    results = []
    
    # Calculate days in month
    _, days_in_month = calendar.monthrange(year, month)
    
    for emp in employees:
        s = emp.salary_structure
        if not s or s.basic_salary <= 0:
            continue # Cannot generate without a salary structure
            
        # Check if payroll already exists
        existing = Payroll.query.filter_by(employee_id=emp.id, month=month, year=year).first()
        if existing:
            continue # Skip if already generated (HR can delete and regenerate if needed)
            
        # 1. Fetch Attendance (just to have metrics, though salary relies on LOP)
        attendances = Attendance.query.filter(
            Attendance.employee_id == emp.id,
            db.extract('month', Attendance.attendance_date) == month,
            db.extract('year', Attendance.attendance_date) == year
        ).all()
        
        # 2. Calculate LOP (Loss of Pay) Leaves
        # Any leave with type "Loss Of Pay" or unpaid absence
        # For simplicity, we query leaves in that month that are LOP and approved
        leaves = Leave.query.filter(
            Leave.employee_id == emp.id,
            Leave.status == 'approved',
            db.extract('month', Leave.from_date) == month,
            db.extract('year', Leave.from_date) == year
        ).all()
        
        lop_days = 0
        for lv in leaves:
            if lv.leave_type and lv.leave_type.name.lower() == 'loss of pay':
                # Calculate days overlap with current month
                start = max(lv.from_date, datetime(year, month, 1).date())
                end = min(lv.to_date, datetime(year, month, days_in_month).date())
                days = (end - start).days + 1
                lop_days += max(0, days)
                
        # 3. Calculate Earnings
        per_day_basic = s.basic_salary / days_in_month
        lop_deduction = lop_days * per_day_basic
        
        actual_basic = max(0, s.basic_salary - lop_deduction)
        
        allowances = s.hra + s.travel_allowance + s.medical_allowance
        bonus = s.bonus
        
        # Calculate Overtime
        ot_hours = float(overtime_hours_map.get(str(emp.id), 0))
        ot_amount = ot_hours * s.overtime_rate
        
        gross_salary = actual_basic + allowances + bonus + ot_amount
        
        # 4. Calculate Deductions
        fixed_deductions = s.pf + s.professional_tax + s.other_deductions
        # Tax computation (flat 5% if not specified, but we use a manual field in this system to be safe)
        # Actually user said Tax, we'll assume a flat 5% on gross if no explicit field exists, 
        # but let's implement a standard 5% tax if gross > 20000 for realism.
        tax = 0
        if gross_salary > 20000:
            tax = gross_salary * 0.05
            
        total_deductions = fixed_deductions + tax
        
        # 5. Net Salary
        net_salary = max(0, gross_salary - total_deductions)
        
        # 6. Create Record
        payroll = Payroll()
        payroll.employee_id = emp.id
        payroll.month = month
        payroll.year = year
        payroll.basic_salary = actual_basic
        payroll.allowances = allowances
        payroll.bonus = bonus
        payroll.overtime_amount = ot_amount
        payroll.gross_salary = gross_salary
        payroll.deductions = fixed_deductions
        payroll.tax = tax
        payroll.net_salary = net_salary
        payroll.status = 'processed'
        db.session.add(payroll)
        results.append(payroll.id)
        
    db.session.commit()
    
    # Auto-generate payslips for the generated payrolls
    from routes.payslip import create_payslip_pdf
    for pr_id in results:
        pr = Payroll.query.get(pr_id)
        if pr:
            try:
                create_payslip_pdf(pr)
            except Exception as e:
                current_app.logger.error(f"Error auto-generating payslip for payroll {pr_id}: {e}")
    
    if len(results) == 0:
        return jsonify(message="0 records generated. Ensure employees have a Salary Structure configured and haven't already been processed for this month."), 400
        
    return jsonify(message=f"Payroll generated for {len(results)} employees", processed=len(results)), 201

@payroll_bp.route('/', methods=['GET'])
@jwt_required()
def get_payrolls():
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    query = Payroll.query
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
        
    payrolls = query.order_by(Payroll.generated_date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'employee_id': p.employee_id,
        'employee_name': f"{p.employee.first_name} {p.employee.last_name}",
        'department': p.employee.department.name if p.employee.department else 'N/A',
        'month': p.month,
        'year': p.year,
        'gross_salary': p.gross_salary,
        'deductions': p.deductions + p.tax,
        'net_salary': p.net_salary,
        'status': p.status,
        'generated_date': p.generated_date.strftime('%Y-%m-%d %H:%M')
    } for p in payrolls]), 200

@payroll_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def delete_payroll(id):
    p = Payroll.query.get_or_404(id)
    db.session.delete(p)
    db.session.commit()
    return jsonify(message="Payroll record deleted successfully"), 200

@payroll_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def dashboard_stats():
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    payrolls = Payroll.query.filter_by(month=month, year=year).all()
    total_expense = sum(p.gross_salary for p in payrolls)
    processed_count = len(payrolls)
    
    active_emps = Employee.query.filter_by(status='active').count()
    pending_count = max(0, active_emps - processed_count)
    
    return jsonify({
        'total_expense': total_expense,
        'processed_count': processed_count,
        'pending_count': pending_count,
        'total_employees': active_emps
    }), 200

@payroll_bp.route('/export/excel', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def export_excel():
    from utils.excel import generate_excel_report
    from flask import send_file
    
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    query = Payroll.query
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
        
    payrolls = query.order_by(Payroll.generated_date.desc()).all()
    
    headers = ["Payroll ID", "Employee Name", "Department", "Period", "Gross Salary", "Deductions", "Net Salary", "Status", "Generated On"]
    data = []
    
    for p in payrolls:
        period_str = f"{p.month}/{p.year}"
        data.append([
            f"PR-{p.id:04d}",
            f"{p.employee.first_name} {p.employee.last_name}",
            p.employee.department.name if p.employee.department else "N/A",
            period_str,
            f"Rs. {p.gross_salary:,.2f}",
            f"Rs. {(p.deductions + p.tax):,.2f}",
            f"Rs. {p.net_salary:,.2f}",
            p.status.upper(),
            p.generated_date.strftime('%Y-%m-%d %H:%M:%S')
        ])
        
    excel_file = generate_excel_report("Payroll Report", headers, data)
    
    return send_file(
        excel_file,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='Payroll_Report.xlsx'
    )
