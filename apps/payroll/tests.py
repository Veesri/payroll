from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, datetime
from django.utils import timezone
from employees.models import Employee, Department, Designation
from leaves.models import LeaveType, Leave
from attendance.models import Attendance
from .models import PayrollPeriod, Holiday, Payroll
from .services import calculate_working_days, process_payroll_for_employee

User = get_user_model()

class PayrollEngineTestCase(TestCase):
    def setUp(self):
        # 1. Create structure
        self.dept = Department.objects.create(name="Engineering", code="ENG")
        self.desig = Designation.objects.create(title="Software Engineer", code="SE")
        
        # 2. Create users
        self.hr_user = User.objects.create_user(
            username="test_hr", password="password", role="HRAdmin", email="hr@test.com"
        )
        self.emp_user = User.objects.create_user(
            username="test_emp", password="password", role="Employee", email="emp@test.com"
        )
        
        # 3. Create employee profile
        self.employee = Employee.objects.create(
            user=self.emp_user,
            employee_code="EMP-101",
            department=self.dept,
            designation=self.desig,
            date_of_joining=date(2026, 1, 1),
            basic_salary=30000.00, # Basic Salary
            hra=6000.00,
            da=3000.00,
            travel_allowance=1000.00,
            medical_allowance=1000.00
        )
        
        # 4. Create period (June 2026: 30 days, 22 working days)
        self.period = PayrollPeriod.objects.create(
            name="June 2026",
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 30)
        )
        
        # 5. Create official holidays
        Holiday.objects.create(name="Holiday 1", date=date(2026, 6, 19)) # Friday

    def test_calculate_working_days(self):
        # June 2026 has:
        # Weekends: 6, 7, 13, 14, 20, 21, 27, 28 (8 days)
        # Holiday: June 19 (1 day)
        # Standard working days: 30 - 8 - 1 = 21 days
        working_days = calculate_working_days(self.period.start_date, self.period.end_date)
        self.assertEqual(working_days, 21)

    def test_payroll_calculations_standard(self):
        # If employee worked all working days (21 days) with no lates and no overtime:
        # Basic: 30000
        # HRA: 6000
        # DA: 3000
        # Travel: 1000
        # Medical: 1000
        # Total Earnings: 41000
        
        # Deductions:
        # PF: 12% of basic = 3600
        # ESI: 0.75% of basic = 225
        # PT: basic > 25000 -> 200
        # Income Tax (TDS): annual basic = 360000 -> 10% of basic = 3000
        # Total Deductions: 3600 + 225 + 200 + 3000 = 7025
        # Net Salary: 41000 - 7025 = 33975
        
        # Seed present attendances for all 21 working days in June 2026
        # We can simulate this by mocking the calculation with 21 present days
        # Let's seed 21 attendance records
        curr_date = self.period.start_date
        holidays = [date(2026, 6, 19)]
        while curr_date <= self.period.end_date:
            if curr_date.weekday() not in [5, 6] and curr_date not in holidays:
                Attendance.objects.create(
                    employee=self.employee,
                    date=curr_date,
                    check_in=datetime.combine(curr_date, datetime.min.time()),
                    check_out=datetime.combine(curr_date, datetime.min.time()) + timezone.timedelta(hours=8),
                    total_hours=8.0,
                    status="Present",
                    qr_verified=True
                )
            curr_date += timezone.timedelta(days=1)
            
        payroll = process_payroll_for_employee(self.employee, self.period, self.hr_user)
        
        self.assertEqual(float(payroll.basic_salary), 30000.00)
        self.assertEqual(float(payroll.pf_deduction), 3600.00)
        self.assertEqual(float(payroll.esi_deduction), 225.00)
        self.assertEqual(float(payroll.professional_tax), 200.00)
        self.assertEqual(float(payroll.income_tax), 3000.00)
        self.assertEqual(float(payroll.leave_deductions), 0.00)
        self.assertEqual(float(payroll.net_salary), 33975.00)

    def test_payroll_calculations_with_lates_and_unpaid_leaves(self):
        # Let's seed 15 days present, 4 days absent/unpaid, 4 late entries
        # Standard working days: 21 days
        # Attendance Factor: 17 present days (let's say 17 present days)
        # Unpaid days: 21 - 17 = 4 days
        # Leave deductions: 4 * (30000 / 21) = 5714.29
        # Lates: 4 lates -> 4 - 3 = 1 late penalized * 10 = 10.00
        
        curr_date = self.period.start_date
        holidays = [date(2026, 6, 19)]
        present_count = 0
        late_count = 0
        
        while curr_date <= self.period.end_date:
            if curr_date.weekday() not in [5, 6] and curr_date not in holidays:
                if present_count < 17:
                    is_late = (late_count < 4)
                    status = "Late" if is_late else "Present"
                    Attendance.objects.create(
                        employee=self.employee,
                        date=curr_date,
                        check_in=datetime.combine(curr_date, datetime.min.time()),
                        check_out=datetime.combine(curr_date, datetime.min.time()) + timezone.timedelta(hours=8),
                        total_hours=8.0,
                        is_late=is_late,
                        status=status,
                        qr_verified=True
                    )
                    present_count += 1
                    if is_late:
                        late_count += 1
            curr_date += timezone.timedelta(days=1)
            
        payroll = process_payroll_for_employee(self.employee, self.period, self.hr_user)
        
        # Assertions
        self.assertEqual(float(payroll.late_penalties), 10.00)
        # Leave deductions: 4 * 1428.5714... = 5714.29
        self.assertAlmostEqual(float(payroll.leave_deductions), 5714.29, places=2)
