from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group

@receiver(post_migrate)
def create_default_roles(sender, **kwargs):
    # Only run for our accounts app
    if sender.name == 'accounts':
        roles = ['SuperAdmin', 'HRAdmin', 'PayrollOfficer', 'DeptManager', 'Employee']
        for role_name in roles:
            Group.objects.get_or_create(name=role_name)
        print("Default roles/groups successfully seeded.")
