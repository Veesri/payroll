from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False) # 'super_admin', 'hr_admin', 'employee'
    is_active = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    
    employee = db.relationship('Employee', backref='user', uselist=False)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    head_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    employees = db.relationship('Employee', backref='department', foreign_keys='Employee.department_id')

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    designation = db.Column(db.String(100))
    status = db.Column(db.String(50), default='active') # 'active', 'inactive', 'on_leave'
    photo_url = db.Column(db.String(255))
    join_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    documents = db.relationship('EmployeeDocument', backref='employee', lazy=True)
    attendances = db.relationship('Attendance', backref='employee', lazy=True)
    leaves = db.relationship('Leave', backref='employee', lazy=True)
    salary_structure = db.relationship('SalaryStructure', backref='employee', uselist=False)

class EmployeeDocument(db.Model):
    __tablename__ = 'employee_documents'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    document_name = db.Column(db.String(100), nullable=False)
    document_url = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    attendance_date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time)
    check_out = db.Column(db.Time)
    status = db.Column(db.String(50)) # 'present', 'absent', 'half_day', 'late', 'leave'
    working_hours = db.Column(db.Float)
    attendance_source = db.Column(db.String(50)) # 'web', 'qr', 'manual'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LeaveType(db.Model):
    __tablename__ = 'leave_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False) # 'casual', 'sick', 'earned', 'loss_of_pay'
    days_allowed = db.Column(db.Integer, nullable=False)

class Leave(db.Model):
    __tablename__ = 'leaves'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    leave_type_id = db.Column(db.Integer, db.ForeignKey('leave_types.id'), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), default='pending') # 'pending', 'approved', 'rejected'
    reason = db.Column(db.Text)
    
    # Hierarchy Fields
    requested_by_role = db.Column(db.String(50), default='employee')
    approval_level = db.Column(db.String(50), default='hr_admin')
    approved_by_role = db.Column(db.String(50), nullable=True)
    
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    comments = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    leave_type = db.relationship('LeaveType')

class SalaryStructure(db.Model):
    __tablename__ = 'salary_structures'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    hra = db.Column(db.Float, default=0.0)
    travel_allowance = db.Column(db.Float, default=0.0)
    medical_allowance = db.Column(db.Float, default=0.0)
    bonus = db.Column(db.Float, default=0.0)
    pf = db.Column(db.Float, default=0.0)
    professional_tax = db.Column(db.Float, default=0.0)
    other_deductions = db.Column(db.Float, default=0.0)
    overtime_rate = db.Column(db.Float, default=0.0) # Rate per hour
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Payroll(db.Model):
    __tablename__ = 'payroll'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, default=0.0)
    bonus = db.Column(db.Float, default=0.0)
    overtime_amount = db.Column(db.Float, default=0.0)
    gross_salary = db.Column(db.Float, nullable=False)
    deductions = db.Column(db.Float, default=0.0)
    tax = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='draft') # 'draft', 'processed'
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='payrolls')

class Payslip(db.Model):
    __tablename__ = 'payslips'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False)
    payroll_id = db.Column(db.Integer, db.ForeignKey('payroll.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    pdf_path = db.Column(db.String(255), nullable=False)
    email_sent = db.Column(db.Boolean, default=False)
    generated_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='payslips')
    payroll = db.relationship('Payroll', backref='payslip', uselist=False)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
