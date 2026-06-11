import os
import django
from datetime import date, datetime, timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'payroll_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from employees.models import Employee, Department, Designation
from leaves.models import LeaveType, LeaveBalance, Leave
from payroll.models import PayrollPeriod, Holiday, PayrollAdjustment
from attendance.models import Attendance

User = get_user_model()

def seed():
    print("Seeding database...")
    
    # 1. Create Departments
    eng_dept, _ = Department.objects.get_or_create(name="Engineering", code="ENG")
    hr_dept, _ = Department.objects.get_or_create(name="Human Resources", code="HR")
    fin_dept, _ = Department.objects.get_or_create(name="Finance", code="FIN")
    
    # 2. Create Designations
    se_desig, _ = Designation.objects.get_or_create(title="Software Engineer", code="SE")
    mgr_desig, _ = Designation.objects.get_or_create(title="Engineering Manager", code="EM")
    hr_desig, _ = Designation.objects.get_or_create(title="HR Director", code="HRD")
    
    # 3. Create Users & Employees
    # Admin (HRAdmin)
    if not User.objects.filter(username="admin").exists():
        admin_user = User.objects.create_superuser(
            username="admin",
            password="adminpassword",
            email="admin@veesri.com",
            first_name="Alice",
            last_name="Smith",
            role="HRAdmin"
        )
        # Create profile
        Employee.objects.create(
            user=admin_user,
            employee_code="EMP-000",
            department=hr_dept,
            designation=hr_desig,
            date_of_joining=date(2025, 1, 1),
            basic_salary=90000.00,
            hra=18000.00,
            da=9000.00,
            travel_allowance=4000.00,
            medical_allowance=3000.00
        )
        print("Admin user created.")

    # Manager (DeptManager)
    if not User.objects.filter(username="manager").exists():
        mgr_user = User.objects.create_user(
            username="manager",
            password="managerpassword",
            email="manager@veesri.com",
            first_name="Bob",
            last_name="Jones",
            role="DeptManager"
        )
        eng_mgr = Employee.objects.create(
            user=mgr_user,
            employee_code="EMP-001",
            department=eng_dept,
            designation=mgr_desig,
            date_of_joining=date(2025, 3, 1),
            basic_salary=75000.00,
            hra=15000.00,
            da=7500.00,
            travel_allowance=3000.00,
            medical_allowance=3000.00
        )
        # Set department manager relation
        eng_dept.manager_user = mgr_user
        eng_dept.save()
        print("Manager user created.")

    # Regular Employee
    if not User.objects.filter(username="employee").exists():
        emp_user = User.objects.create_user(
            username="employee",
            password="employeepassword",
            email="developer@veesri.com",
            first_name="Charlie",
            last_name="Brown",
            role="Employee"
        )
        emp_profile = Employee.objects.create(
            user=emp_user,
            employee_code="EMP-002",
            department=eng_dept,
            designation=se_desig,
            date_of_joining=date(2025, 6, 1),
            basic_salary=45000.00,
            hra=9000.00,
            da=4500.00,
            travel_allowance=2000.00,
            medical_allowance=2000.00
        )
        print("Employee user created.")

    # 4. Create Leave Types
    cl_type, _ = LeaveType.objects.get_or_create(name="Casual Leave", code="CL", max_days_per_year=12, is_paid=True)
    sl_type, _ = LeaveType.objects.get_or_create(name="Sick Leave", code="SL", max_days_per_year=10, is_paid=True)
    el_type, _ = LeaveType.objects.get_or_create(name="Earned Leave", code="EL", max_days_per_year=15, is_paid=True)
    
    # 5. Leave Balances Allocation for 2026
    year = 2026
    for emp in Employee.objects.all():
        for lt in [cl_type, sl_type, el_type]:
            LeaveBalance.objects.get_or_create(
                employee=emp,
                leave_type=lt,
                year=year,
                defaults={
                    'allocated_days': lt.max_days_per_year,
                    'used_days': 0.0
                }
            )
            
    # 6. Create Payroll Period for June 2026
    period, _ = PayrollPeriod.objects.get_or_create(
        name="June 2026",
        start_date=date(2026, 6, 1),
        end_date=date(2026, 6, 30)
    )
    
    # 7. Create system holidays
    Holiday.objects.get_or_create(name="Juneteenth Holiday", date=date(2026, 6, 19))
    
    # 8. Create some Attendance Logs for EMP-002 (Charlie Brown)
    charlie = Employee.objects.get(employee_code="EMP-002")
    
    # Seed 10 working days in June 2026
    log_dates = [
        (date(2026, 6, 1), datetime(2026, 6, 1, 9, 0), datetime(2026, 6, 1, 18, 0), "Present"),
        (date(2026, 6, 2), datetime(2026, 6, 2, 9, 15), datetime(2026, 6, 2, 17, 30), "Present"), # worked 8.25h
        (date(2026, 6, 3), datetime(2026, 6, 3, 9, 45), datetime(2026, 6, 3, 18, 0), "Late"), # late entry
        (date(2026, 6, 4), datetime(2026, 6, 4, 9, 0), datetime(2026, 6, 4, 20, 0), "Present"), # worked 11h (overtime!)
        (date(2026, 6, 5), datetime(2026, 6, 5, 9, 0), datetime(2026, 6, 5, 13, 0), "HalfDay"),
        (date(2026, 6, 8), datetime(2026, 6, 8, 9, 0), datetime(2026, 6, 8, 18, 0), "Present"),
        (date(2026, 6, 9), datetime(2026, 6, 9, 9, 0), datetime(2026, 6, 9, 18, 0), "Present"),
        (date(2026, 6, 10), datetime(2026, 6, 10, 9, 0), datetime(2026, 6, 10, 18, 0), "Present"),
    ]
    
    for d, ci, co, stat in log_dates:
        # Calculate total hours worked
        tot_hrs = (co - ci).total_seconds() / 3600.0
        
        Attendance.objects.get_or_create(
            employee=charlie,
            date=d,
            defaults={
                'check_in': ci,
                'check_out': co,
                'total_hours': tot_hrs,
                'is_late': stat == "Late",
                'status': stat,
                'qr_verified': True
            }
        )
        
    print("Database seeding completed successfully.")

if __name__ == '__main__':
    seed()
