from django.db import models
from django.conf import settings
from employees.models import Employee

class Attendance(models.Model):
    STATUS_CHOICES = (
        ('Present', 'Present'),
        ('HalfDay', 'HalfDay'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Present')
    total_hours = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    is_late = models.BooleanField(default=False)
    qr_verified = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'date')

    def calculate_hours_and_status(self):
        """Calculates total working hours and checks late arrival based on shift start."""
        if not self.check_in:
            return
        
        # Calculate working hours
        if self.check_out:
            duration = self.check_out - self.check_in
            hours = duration.total_seconds() / 3600.0
            self.total_hours = round(hours, 2)
            
            # Determine status based on working hours
            if self.total_hours >= 8.0:
                self.status = 'Present'
            elif self.total_hours >= 4.0:
                self.status = 'HalfDay'
            else:
                self.status = 'Absent'
        else:
            # Checked in but not checked out yet
            self.total_hours = 0.00
            self.status = 'Present'

        # Rule: Late if check-in time is past 09:30 AM on that day
        # Let's extract local check-in hour/minute
        local_time = self.check_in
        if local_time.hour > 9 or (local_time.hour == 9 and local_time.minute > 30):
            self.is_late = True
            # Keep late status unless worked less than half day
            if self.status == 'Present':
                self.status = 'Late'

    def save(self, *args, **kwargs):
        self.calculate_hours_and_status()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.employee_code} - {self.date} - {self.status}"

class AttendanceCorrection(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='corrections')
    requested_check_in = models.DateTimeField()
    requested_check_out = models.DateTimeField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_corrections'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Correction request for {self.attendance.employee.employee_code} on {self.attendance.date}"
