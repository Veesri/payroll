import json
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone

from employees.models import Employee, Department, Designation
from attendance.models import Attendance, AttendanceCorrection
from leaves.models import Leave, LeaveBalance, LeaveType
from payroll.models import PayrollPeriod, Payroll, Holiday
from payslips.models import Payslip
from .models import AuditLog

@login_required
def dashboard_view(request):
    user = request.user
    
    # 1. Aggregations for widgets
    total_employees = Employee.objects.count()
    
    # Latest period total cost
    latest_payroll_sum = 0
    latest_period = PayrollPeriod.objects.order_by('-start_date').first()
    if latest_period:
        latest_payroll_sum = Payroll.objects.filter(period=latest_period).aggregate(s=Sum('net_salary'))['s'] or 0
        
    pending_leaves = Leave.objects.filter(status='Pending').count()
    present_today = Attendance.objects.filter(date=date.today(), status__in=['Present', 'Late', 'HalfDay']).count()
    
    # 2. Charts Data (Monthly Payroll Costs)
    periods = PayrollPeriod.objects.order_by('start_date')[:6]
    chart_labels = []
    chart_data = []
    
    for p in periods:
        chart_labels.append(p.name)
        sum_val = Payroll.objects.filter(period=p).aggregate(s=Sum('net_salary'))['s'] or 0
        chart_data.append(float(sum_val))
        
    # Department distribution chart data
    dept_distribution = Employee.objects.values('department__name').annotate(count=Count('id'))
    dept_labels = [item['department__name'] or 'Unassigned' for item in dept_distribution]
    dept_counts = [item['count'] for item in dept_distribution]
    
    context = {
        'total_employees': total_employees,
        'total_payroll_costs': latest_payroll_sum,
        'pending_leaves': pending_leaves,
        'present_today': present_today,
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'dept_labels': json.dumps(dept_labels),
        'dept_counts': json.dumps(dept_counts),
        'latest_period_name': latest_period.name if latest_period else 'No active periods'
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def employees_list_view(request):
    # Only HR and Admin
    if request.user.role not in ['HRAdmin', 'SuperAdmin']:
        messages.error(request, "Permission Denied.")
        return redirect('dashboard')
        
    employees = Employee.objects.select_related('user', 'department', 'designation').all()
    departments = Department.objects.all()
    designations = Designation.objects.all()
    
    # Handle creation post
    if request.method == 'POST':
        # Simple creation logic
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role', 'Employee')
        
        emp_code = request.POST.get('employee_code')
        dept_id = request.POST.get('department')
        desig_id = request.POST.get('designation')
        doj = request.POST.get('date_of_joining')
        basic_sal = request.POST.get('basic_salary', 0)
        hra = request.POST.get('hra', 0)
        da = request.POST.get('da', 0)
        travel = request.POST.get('travel', 0)
        medical = request.POST.get('medical', 0)
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        try:
            # Create user
            new_user = User.objects.create_user(
                username=username, 
                password=password, 
                email=email,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Create employee
            employee = Employee.objects.create(
                user=new_user,
                employee_code=emp_code,
                department_id=dept_id or None,
                designation_id=desig_id or None,
                date_of_joining=doj,
                basic_salary=basic_sal,
                hra=hra,
                da=da,
                travel_allowance=travel,
                medical_allowance=medical
            )
            
            # Allocate initial leave balances for standard types
            leave_types = LeaveType.objects.all()
            year = date.today().year
            for lt in leave_types:
                LeaveBalance.objects.create(
                    employee=employee,
                    leave_type=lt,
                    year=year,
                    allocated_days=lt.max_days_per_year,
                    used_days=0.0
                )
                
            messages.success(request, f"Employee profile created successfully for {new_user.get_full_name()}. Allocated default leaves.")
            return redirect('employees_list')
        except Exception as e:
            messages.error(request, f"Error creating employee: {e}")
            
    return render(request, 'core/employees.html', {
        'employees': employees,
        'departments': departments,
        'designations': designations
    })

@login_required
def attendance_dashboard_view(request):
    user = request.user
    
    # Resolve Employee profile
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        employee = None
        
    today = date.today()
    today_att = None
    if employee:
        today_att = Attendance.objects.filter(employee=employee, date=today).first()
        
    # Get corrections list for Manager / HR review
    pending_corrections = []
    if user.role in ['HRAdmin', 'SuperAdmin']:
        pending_corrections = AttendanceCorrection.objects.filter(status='Pending').select_related('attendance__employee__user')
    elif user.role == 'DeptManager':
        pending_corrections = AttendanceCorrection.objects.filter(
            attendance__employee__department__manager_user=user, 
            status='Pending'
        ).select_related('attendance__employee__user')
        
    # Standard log view
    if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
        att_logs = Attendance.objects.all().order_by('-date')[:50]
    elif user.role == 'DeptManager':
        att_logs = Attendance.objects.filter(employee__department__manager_user=user).order_by('-date')[:50]
    else:
        att_logs = Attendance.objects.filter(employee=employee).order_by('-date')[:50]
        
    return render(request, 'core/attendance.html', {
        'employee': employee,
        'today_att': today_att,
        'pending_corrections': pending_corrections,
        'att_logs': att_logs
    })

@login_required
def leaves_list_view(request):
    user = request.user
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        employee = None
        
    year = date.today().year
    
    # Leave Balances
    balances = []
    if employee:
        balances = LeaveBalance.objects.filter(employee=employee, year=year).select_related('leave_type')
        
    # Leave Requests Table
    if user.role in ['HRAdmin', 'SuperAdmin']:
        leaves = Leave.objects.all().order_by('-start_date')
    elif user.role == 'DeptManager':
        # manager gets requests for their department + their own
        leaves = Leave.objects.filter(employee__department__manager_user=user).order_by('-start_date')
    else:
        leaves = Leave.objects.filter(employee=employee).order_by('-start_date')
        
    # Handle Apply Leave post
    if request.method == 'POST' and employee:
        leave_type_id = request.POST.get('leave_type')
        start_str = request.POST.get('start_date')
        end_str = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        try:
            start_date = date.fromisoformat(start_str)
            end_date = date.fromisoformat(end_str)
            duration = (end_date - start_date).days + 1
            
            leave_type = LeaveType.objects.get(id=leave_type_id)
            balance = LeaveBalance.objects.get(employee=employee, leave_type=leave_type, year=start_date.year)
            
            if balance.remaining_days < duration:
                messages.error(request, f"Insufficient leaves balance. Available: {balance.remaining_days}, Requested: {duration}")
            elif start_date > end_date:
                messages.error(request, "Start date cannot be after end date.")
            else:
                Leave.objects.create(
                    employee=employee,
                    leave_type=leave_type,
                    start_date=start_date,
                    end_date=end_date,
                    reason=reason
                )
                messages.success(request, f"Leave application submitted successfully for {duration} days.")
                return redirect('leaves_list')
        except Exception as e:
            messages.error(request, f"Error applying for leave: {e}")
            
    leave_types = LeaveType.objects.all()
    return render(request, 'core/leaves.html', {
        'balances': balances,
        'leaves': leaves,
        'leave_types': leave_types,
        'employee': employee
    })

@login_required
def payroll_process_view(request):
    if request.user.role not in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
        messages.error(request, "Permission Denied.")
        return redirect('dashboard')
        
    periods = PayrollPeriod.objects.all().order_by('-start_date')
    holidays = Holiday.objects.all().order_by('-date')
    
    # Handle Holiday adding
    if request.method == 'POST' and 'add_holiday' in request.POST:
        name = request.POST.get('name')
        date_str = request.POST.get('date')
        try:
            Holiday.objects.create(name=name, date=date_str)
            messages.success(request, f"Holiday '{name}' added successfully.")
            return redirect('payroll_process')
        except Exception as e:
            messages.error(request, f"Error adding holiday: {e}")
            
    # Handle Period creation
    if request.method == 'POST' and 'create_period' in request.POST:
        name = request.POST.get('name')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        try:
            PayrollPeriod.objects.create(name=name, start_date=start, end_date=end)
            messages.success(request, f"Payroll Period '{name}' created.")
            return redirect('payroll_process')
        except Exception as e:
            messages.error(request, f"Error creating period: {e}")
            
    return render(request, 'core/payroll.html', {
        'periods': periods,
        'holidays': holidays
    })

@login_required
def payslips_list_view(request):
    user = request.user
    
    # Find employee profile
    try:
        employee = user.employee_profile
    except Employee.DoesNotExist:
        employee = None
        
    if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
        payslips = Payslip.objects.select_related('payroll__employee__user', 'payroll__period').all().order_by('-payroll__period__start_date')
    else:
        payslips = Payslip.objects.filter(payroll__employee=employee).select_related('payroll__period').order_by('-payroll__period__start_date')
        
    return render(request, 'core/payslips.html', {
        'payslips': payslips
    })

@login_required
def audit_logs_view(request):
    if request.user.role not in ['HRAdmin', 'SuperAdmin']:
        messages.error(request, "Permission Denied.")
        return redirect('dashboard')
        
    logs = AuditLog.objects.select_related('user').all().order_by('-timestamp')[:100]
    return render(request, 'core/audit_logs.html', {
        'logs': logs
    })
