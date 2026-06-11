from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    ROLE_CHOICES = (
        ('SuperAdmin', 'SuperAdmin'),
        ('HRAdmin', 'HRAdmin'),
        ('PayrollOfficer', 'PayrollOfficer'),
        ('DeptManager', 'DeptManager'),
        ('Employee', 'Employee'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Employee')
    is_locked = models.BooleanField(default=False)
    failed_login_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    last_ip = models.CharField(max_length=45, null=True, blank=True)
    
    def check_lockout(self):
        """Checks if the user's lockout period has expired and unlocks if so."""
        if self.is_locked and self.locked_until:
            if timezone.now() > self.locked_until:
                self.is_locked = False
                self.failed_login_attempts = 0
                self.locked_until = None
                self.save()
        return self.is_locked

    def register_failed_attempt(self):
        """Increments failed attempts and locks the account if limit is reached."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:
            self.is_locked = True
            self.locked_until = timezone.now() + timezone.timedelta(minutes=15)
        self.save()

    def reset_failed_attempts(self):
        """Resets failed login count."""
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
        self.save()

    def __str__(self):
        return f"{self.username} ({self.role})"
