from datetime import timedelta, date
from django.db.models import Sum
from .models import PayrollPeriod, Payroll, PayrollAdjustment, Holiday
from attendance.models import Attendance
from leaves.models import Leave
from employees.models import Employee

def calculate_working_days(start_date, end_date):
    """Calculates total standard working days excluding weekends and official Holidays."""
    curr_date = start_date
    working_days = 0
    holidays = set(Holiday.objects.filter(date__range=(start_date, end_date)).values_list('date', flat=True))
    
    while curr_date <= end_date:
        # 5 = Saturday, 6 = Sunday
        if curr_date.weekday() not in [5, 6] and curr_date not in holidays:
            working_days += 1
        curr_date += timedelta(days=1)
        
    return working_days

def process_payroll_for_employee(employee, period, operator_user=None):
    """Calculates and generates/updates a Payroll record for a single employee."""
    start_date = period.start_date
    end_date = period.end_date
    
    # 1. Total standard working days in the month
    standard_working_days = calculate_working_days(start_date, end_date)
    if standard_working_days == 0:
        standard_working_days = 22 # fallback to avoid division by zero
        
    # 2. Query attendance
    attendances = Attendance.objects.filter(employee=employee, date__range=(start_date, end_date))
    days_present = 0.0
    late_entries = 0
    overtime_hours = 0.0
    
    for att in attendances:
        if att.status in ['Present', 'Late']:
            days_present += 1.0
        elif att.status == 'HalfDay':
            days_present += 0.5
            
        if att.is_late:
            late_entries += 1
            
        if att.total_hours > 8.5:
            overtime_hours += float(att.total_hours - 8.0)
            
    # 3. Query approved paid leaves in the period
    # We sum up duration of approved paid leaves falling in this range
    leaves = Leave.objects.filter(
        employee=employee,
        status='Approved',
        leave_type__is_paid=True,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    paid_leave_days = 0.0
    for leave in leaves:
        # Find overlap days
        overlap_start = max(leave.start_date, start_date)
        overlap_end = min(leave.end_date, end_date)
        overlap_days = (overlap_end - overlap_start).days + 1
        paid_leave_days += float(overlap_days)
        
    # 4. Attendance factor & Unpaid days
    attendance_factor = days_present + paid_leave_days
    unpaid_days = float(standard_working_days) - attendance_factor
    if unpaid_days < 0.0:
        unpaid_days = 0.0
        
    # 5. Math Calculations
    basic = float(employee.basic_salary)
    hra = float(employee.hra)
    da = float(employee.da)
    travel = float(employee.travel_allowance)
    medical = float(employee.medical_allowance)
    
    # Leave deductions
    leave_deductions = unpaid_days * (basic / standard_working_days)
    
    # Late Penalty: $10 for every late entry after the first 3
    late_penalties = max(0, late_entries - 3) * 10.0
    
    # Overtime Pay: hourly rate * 1.5 * overtime_hours
    hourly_rate = (basic / standard_working_days) / 8.0
    overtime_pay = overtime_hours * hourly_rate * 1.5
    
    # Statutory Deductions
    pf_deduction = basic * 0.12
    esi_deduction = basic * 0.0075
    
    # Professional Tax
    if basic > 25000:
        professional_tax = 200.0
    elif basic > 15000:
        professional_tax = 150.0
    else:
        professional_tax = 0.0
        
    # Income Tax (TDS)
    annual_basic = basic * 12
    if annual_basic > 600000:
        income_tax = basic * 0.20
    elif annual_basic > 300000:
        income_tax = basic * 0.10
    else:
        income_tax = 0.0
        
    # 6. Adjustments (Allowance / Deduction)
    adjustments = PayrollAdjustment.objects.filter(employee=employee, period=period)
    allowances_sum = float(adjustments.filter(type='Allowance').aggregate(s=Sum('amount'))['s'] or 0.0)
    deductions_sum = float(adjustments.filter(type='Deduction').aggregate(s=Sum('amount'))['s'] or 0.0)
    other_adjustments = allowances_sum - deductions_sum
    
    # Net Salary formula
    earnings = basic + hra + da + travel + medical + overtime_pay + allowances_sum
    deductions = pf_deduction + esi_deduction + professional_tax + income_tax + leave_deductions + late_penalties + deductions_sum
    
    net_salary = earnings - deductions
    if net_salary < 0.0:
        net_salary = 0.0
        
    # 7. Save to model
    payroll, created = Payroll.objects.update_or_create(
        employee=employee,
        period=period,
        defaults={
            'basic_salary': employee.basic_salary,
            'hra': employee.hra,
            'da': employee.da,
            'travel_allowance': employee.travel_allowance,
            'medical_allowance': employee.medical_allowance,
            'bonus': allowances_sum,  # Map total allowances sum to bonus field
            'overtime_pay': round(overtime_pay, 2),
            'pf_deduction': round(pf_deduction, 2),
            'esi_deduction': round(esi_deduction, 2),
            'professional_tax': round(professional_tax, 2),
            'income_tax': round(income_tax, 2),
            'leave_deductions': round(leave_deductions, 2),
            'late_penalties': round(late_penalties, 2),
            'other_adjustments': round(other_adjustments, 2),
            'net_salary': round(net_salary, 2),
            'processed_by': operator_user
        }
    )
    return payroll
