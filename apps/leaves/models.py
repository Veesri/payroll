from django.db import models
from django.conf import settings
from employees.models import Employee

class LeaveType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    code = models.CharField(max_length=10, unique=True)
    max_days_per_year = models.IntegerField(default=12)
    is_paid = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances')
    year = models.IntegerField()
    allocated_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    used_days = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    @property
    def remaining_days(self):
        return self.allocated_days - self.used_days

    def __str__(self):
        return f"{self.employee.employee_code} - {self.leave_type.name} ({self.year}): {self.remaining_days} left"

class Leave(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='leaves')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    manager_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_approved_leaves'
    )
    manager_approval_date = models.DateTimeField(null=True, blank=True)
    
    hr_approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='hr_approved_leaves'
    )
    hr_approval_date = models.DateTimeField(null=True, blank=True)

    @property
    def duration_days(self):
        # Calculates number of days of the leave (inclusive)
        if self.end_date and self.start_date:
            return (self.end_date - self.start_date).days + 1
        return 0

    def __str__(self):
        return f"{self.employee.employee_code} - {self.leave_type.name}: {self.start_date} to {self.end_date}"
