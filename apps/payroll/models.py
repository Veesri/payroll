from django.db import models
from django.conf import settings
from employees.models import Employee

class PayrollPeriod(models.Model):
    name = models.CharField(max_length=50) # e.g. "June 2026"
    start_date = models.DateField()
    end_date = models.DateField()
    is_locked = models.BooleanField(default=False)
    locked_at = models.DateTimeField(null=True, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='locked_periods'
    )

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

class PayrollAdjustment(models.Model):
    ADJUSTMENT_TYPES = (
        ('Allowance', 'Allowance'),
        ('Deduction', 'Deduction'),
    )
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='adjustments')
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='adjustments')
    type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.employee_code} - {self.name}: {self.type} of {self.amount}"

class Holiday(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField(unique=True)

    def __str__(self):
        return f"{self.name} ({self.date})"

class Payroll(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payrolls')
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payrolls')
    
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    da = models.DecimalField(max_digits=10, decimal_places=2)
    travel_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2)
    
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    pf_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    esi_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    professional_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    income_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    leave_deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    late_penalties = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    other_adjustments = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    net_salary = models.DecimalField(max_digits=10, decimal_places=2)
    processed_at = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_payrolls'
    )

    class Meta:
        unique_together = ('employee', 'period')

    def __str__(self):
        return f"Payroll {self.employee.employee_code} - {self.period.name}: Net {self.net_salary}"
