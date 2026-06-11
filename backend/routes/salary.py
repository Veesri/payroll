from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, SalaryStructure, Employee
from routes.employee import role_required

salary_bp = Blueprint('salary', __name__)

@salary_bp.route('/', methods=['GET'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def get_all_salary_structures():
    employees = Employee.query.all()
    results = []
    for emp in employees:
        s = emp.salary_structure
        if s:
            results.append({
                'employee_id': emp.id,
                'employee_name': f"{emp.first_name} {emp.last_name}",
                'department': emp.department.name if emp.department else 'N/A',
                'structure_id': s.id,
                'basic_salary': s.basic_salary,
                'hra': s.hra,
                'travel_allowance': s.travel_allowance,
                'medical_allowance': s.medical_allowance,
                'bonus': s.bonus,
                'pf': s.pf,
                'professional_tax': s.professional_tax,
                'other_deductions': s.other_deductions,
                'overtime_rate': s.overtime_rate
            })
        else:
            results.append({
                'employee_id': emp.id,
                'employee_name': f"{emp.first_name} {emp.last_name}",
                'department': emp.department.name if emp.department else 'N/A',
                'structure_id': None,
                'basic_salary': 0,
                'hra': 0, 'travel_allowance': 0, 'medical_allowance': 0, 'bonus': 0,
                'pf': 0, 'professional_tax': 0, 'other_deductions': 0, 'overtime_rate': 0
            })
            
    return jsonify(results), 200

@salary_bp.route('/<int:emp_id>', methods=['PUT', 'POST'])
@jwt_required()
@role_required(['hr_admin', 'super_admin'])
def update_salary_structure(emp_id):
    data = request.get_json()
    emp = Employee.query.get_or_404(emp_id)
    
    s = emp.salary_structure
    if not s:
        s = SalaryStructure(employee_id=emp_id, basic_salary=float(data.get('basic_salary', 0)))
        db.session.add(s)
    else:
        s.basic_salary = float(data.get('basic_salary', s.basic_salary))
        
    s.hra = float(data.get('hra', s.hra))
    s.travel_allowance = float(data.get('travel_allowance', s.travel_allowance))
    s.medical_allowance = float(data.get('medical_allowance', s.medical_allowance))
    s.bonus = float(data.get('bonus', s.bonus))
    s.pf = float(data.get('pf', s.pf))
    s.professional_tax = float(data.get('professional_tax', s.professional_tax))
    s.other_deductions = float(data.get('other_deductions', s.other_deductions))
    s.overtime_rate = float(data.get('overtime_rate', s.overtime_rate))
    
    db.session.commit()
    return jsonify(message="Salary structure updated successfully"), 200
