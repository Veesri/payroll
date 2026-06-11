from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import os

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    manager_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments'
    )

    def __str__(self):
        return f"{self.name} ({self.code})"

class Designation(models.Model):
    title = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title

class Employee(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )
    employee_code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    designation = models.ForeignKey(
        Designation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    date_of_joining = models.DateField()
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    hra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    travel_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    medical_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    pan_number = models.CharField(max_length=10, null=True, blank=True)
    pf_account_number = models.CharField(max_length=22, null=True, blank=True)
    esi_number = models.CharField(max_length=17, null=True, blank=True)
    bank_account_number = models.CharField(max_length=20, null=True, blank=True)
    bank_ifsc_code = models.CharField(max_length=11, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_code})"

def validate_document_file(file):
    """Validates MIME type (PDF, JPEG, PNG) and file size (< 5MB)"""
    # Check size
    filesize = file.size
    if filesize > 5 * 1024 * 1024:
        raise ValidationError("Maximum file size allowed is 5MB")

    # Check extension/content type
    ext = os.path.splitext(file.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    if ext not in valid_extensions:
        raise ValidationError("Unsupported file extension. Only PDF, JPG, and PNG are allowed.")

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_name = models.CharField(max_length=100)
    document_file = models.FileField(
        upload_to='employee_docs/',
        validators=[validate_document_file]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_name} - {self.employee.employee_code}"
