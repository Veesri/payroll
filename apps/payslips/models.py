from django.db import models
from payroll.models import Payroll

class Payslip(models.Model):
    payroll = models.OneToOneField(Payroll, on_delete=models.CASCADE, related_name='payslip')
    payslip_code = models.CharField(max_length=30, unique=True)
    pdf_file = models.FileField(upload_to='payslips/', null=True, blank=True)
    is_email_sent = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payslip {self.payslip_code} - {self.payroll.employee.employee_code}"
