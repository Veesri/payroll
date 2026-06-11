import os
import uuid
from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from flask_mail import Message
from models import db, Payslip, Payroll, Employee
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from routes.employee import role_required

payslip_bp = Blueprint('payslip', __name__)

# Ensure directory exists
def get_payslip_dir():
    d = os.path.join(current_app.static_folder, 'payslips')
    os.makedirs(d, exist_ok=True)
    return d

def create_payslip_pdf(payroll):
    emp = payroll.employee
    
    # Check if exists
    existing = Payslip.query.filter_by(payroll_id=payroll.id).first()
    if existing:
        return existing
        
    # Generate PDF
    filename = f"payslip_{emp.id}_{payroll.month}_{payroll.year}_{uuid.uuid4().hex[:8]}.pdf"
    filepath = os.path.join(get_payslip_dir(), filename)
    
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # Header
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 50, "Enterprise HRMS")
    c.setFont("Helvetica", 14)
    month_name = datetime(payroll.year, payroll.month, 1).strftime('%B')
    c.drawCentredString(width/2, height - 70, f"Salary Slip - {month_name} {payroll.year}")
    
    c.line(50, height - 90, width - 50, height - 90)
    
    # Employee Info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 120, "Employee ID:")
    c.drawString(50, height - 140, "Employee Name:")
    c.drawString(50, height - 160, "Department:")
    c.drawString(50, height - 180, "Designation:")
    
    c.setFont("Helvetica", 12)
    c.drawString(160, height - 120, f"EMP-{emp.id:04d}")
    c.drawString(160, height - 140, f"{emp.first_name} {emp.last_name}")
    c.drawString(160, height - 160, emp.department.name if emp.department else 'N/A')
    c.drawString(160, height - 180, emp.designation or 'N/A')
    
    # Earnings & Deductions Table
    c.line(50, height - 210, width - 50, height - 210)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 230, "Earnings")
    c.drawString(width/2 + 20, height - 230, "Deductions")
    c.line(50, height - 240, width - 50, height - 240)
    
    c.setFont("Helvetica", 11)
    # Left column (Earnings)
    c.drawString(50, height - 260, "Basic Salary")
    c.drawRightString(width/2 - 20, height - 260, f"Rs. {payroll.basic_salary:,.2f}")
    c.drawString(50, height - 280, "Allowances (HRA, TA, MA)")
    c.drawRightString(width/2 - 20, height - 280, f"Rs. {payroll.allowances:,.2f}")
    c.drawString(50, height - 300, "Bonus")
    c.drawRightString(width/2 - 20, height - 300, f"Rs. {payroll.bonus:,.2f}")
    c.drawString(50, height - 320, "Overtime")
    c.drawRightString(width/2 - 20, height - 320, f"Rs. {payroll.overtime_amount:,.2f}")
    
    # Right column (Deductions)
    c.drawString(width/2 + 20, height - 260, "Fixed Deductions")
    c.drawRightString(width - 50, height - 260, f"Rs. {payroll.deductions:,.2f}")
    c.drawString(width/2 + 20, height - 280, "Tax")
    c.drawRightString(width - 50, height - 280, f"Rs. {payroll.tax:,.2f}")
    
    # Middle line
    c.line(width/2, height - 210, width/2, height - 360)
    
    # Totals
    c.line(50, height - 360, width - 50, height - 360)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 380, "Gross Earnings")
    c.drawRightString(width/2 - 20, height - 380, f"Rs. {payroll.gross_salary:,.2f}")
    c.drawString(width/2 + 20, height - 380, "Total Deductions")
    c.drawRightString(width - 50, height - 380, f"Rs. {(payroll.deductions + payroll.tax):,.2f}")
    
    c.line(50, height - 400, width - 50, height - 400)
    
    # Net Pay
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 440, "Net Salary Payable:")
    c.drawRightString(width - 50, height - 440, f"Rs. {payroll.net_salary:,.2f}")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawCentredString(width/2, 50, "This is a computer generated document and does not require a signature.")
    
    c.save()
    
    # Save to DB
    payslip = Payslip()
    payslip.employee_id = emp.id
    payslip.payroll_id = payroll.id
    payslip.month = payroll.month
    payslip.year = payroll.year
    payslip.pdf_path = f"/uploads/payslips/{filename}"
    payslip.email_sent = False
    db.session.add(payslip)
    db.session.commit()
    return payslip

@payslip_bp.route('/', methods=['GET'])
@jwt_required()
def get_payslips():
    claims = get_jwt()
    role = claims.get('role')
    user_id = get_jwt_identity()
    
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    # Find employee if role is employee
    emp = None
    if role == 'employee':
        emp = Employee.query.filter_by(user_id=user_id).first()
        if not emp:
            return jsonify([]), 200

    # Self-healing sync: find all processed payrolls and make sure payslips exist
    payroll_query = Payroll.query.filter_by(status='processed')
    if role == 'employee':
        payroll_query = payroll_query.filter_by(employee_id=emp.id)
    
    if month:
        payroll_query = payroll_query.filter_by(month=month)
    if year:
        payroll_query = payroll_query.filter_by(year=year)
        
    payrolls = payroll_query.all()
    for pr in payrolls:
        existing = Payslip.query.filter_by(payroll_id=pr.id).first()
        if not existing:
            try:
                create_payslip_pdf(pr)
            except Exception as e:
                current_app.logger.error(f"Error self-healing payslip for payroll {pr.id}: {e}")
                
    # Now query the payslips database
    query = Payslip.query
    if role == 'employee':
        query = query.filter_by(employee_id=emp.id)
        
    if month:
        query = query.filter_by(month=month)
    if year:
        query = query.filter_by(year=year)
        
    payslips = query.order_by(Payslip.generated_date.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'payroll_id': p.payroll_id,
        'employee_id': p.employee_id,
        'employee_name': f"{p.employee.first_name} {p.employee.last_name}",
        'department': p.employee.department.name if p.employee.department else 'N/A',
        'month': p.month,
        'year': p.year,
        'pdf_path': p.pdf_path,
        'email_sent': p.email_sent,
        'generated_date': p.generated_date.strftime('%Y-%m-%d %H:%M')
    } for p in payslips]), 200

@payslip_bp.route('/generate/<int:payroll_id>', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def generate_payslip(payroll_id):
    payroll = Payroll.query.get_or_404(payroll_id)
    
    # Check if exists
    existing = Payslip.query.filter_by(payroll_id=payroll_id).first()
    if existing:
        return jsonify(message="Payslip already generated", payslip_id=existing.id), 200
        
    payslip = create_payslip_pdf(payroll)
    return jsonify(message="Payslip PDF generated successfully", payslip_id=payslip.id), 201
@payslip_bp.route('/download/<int:id>', methods=['GET'])
@jwt_required()
def download_payslip(id):
    p = Payslip.query.get_or_404(id)
    # Role check
    claims = get_jwt()
    if claims.get('role') == 'employee':
        user_id = get_jwt_identity()
        emp = Employee.query.filter_by(user_id=user_id).first()
        if p.employee_id != emp.id:
            return jsonify(message="Unauthorized"), 403
            
    filepath = os.path.join(current_app.static_folder, p.pdf_path.replace('/uploads/', ''))
    if not os.path.exists(filepath):
        return jsonify(message="PDF file not found on disk"), 404
        
    return send_file(filepath, as_attachment=True)

@payslip_bp.route('/view/<int:id>', methods=['GET'])
@jwt_required()
def view_payslip(id):
    p = Payslip.query.get_or_404(id)
    # Role check
    claims = get_jwt()
    if claims.get('role') == 'employee':
        user_id = get_jwt_identity()
        emp = Employee.query.filter_by(user_id=user_id).first()
        if p.employee_id != emp.id:
            return jsonify(message="Unauthorized"), 403
            
    filepath = os.path.join(current_app.static_folder, p.pdf_path.replace('/uploads/', ''))
    if not os.path.exists(filepath):
        return jsonify(message="PDF file not found on disk"), 404
        
    return send_file(filepath, as_attachment=False, mimetype='application/pdf')

@payslip_bp.route('/email/<int:id>', methods=['POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def email_payslip(id):
    p = Payslip.query.get_or_404(id)
    emp = p.employee
    
    if not emp.email:
        return jsonify(message="Employee has no email address configured"), 400
        
    filepath = os.path.join(current_app.static_folder, p.pdf_path.replace('/uploads/', ''))
    if not os.path.exists(filepath):
        return jsonify(message="PDF file not found on disk. Please generate it first."), 404
        
    month_name = datetime(p.year, p.month, 1).strftime('%B')
    
    msg = Message(
        subject=f"Salary Slip - {month_name} {p.year}",
        recipients=[emp.email],
        body=f"Dear {emp.first_name},\n\nPlease find attached your salary slip for the month of {month_name} {p.year}.\n\nBest Regards,\nHR Department"
    )
    
    with open(filepath, 'rb') as fp:
        msg.attach(os.path.basename(filepath), "application/pdf", fp.read())
        
    try:
        current_app.mail.send(msg)
        print(f"DUMMY EMAIL SENT TO: {emp.email} WITH PDF: {os.path.basename(filepath)}")
        p.email_sent = True
        db.session.commit()
        return jsonify(message="Email sent successfully (Simulated in Dev)"), 200
    except Exception as e:
        return jsonify(message=f"Failed to send email: {str(e)}"), 500
