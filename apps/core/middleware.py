import threading
import json
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
from django.apps import apps
from django.utils import timezone

# Thread-local storage to hold request-level context (User & IP)
_thread_locals = threading.local()

def get_current_user():
    return getattr(_thread_locals, 'user', None)

def get_current_ip():
    return getattr(_thread_locals, 'ip', None)

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store context in thread locals
        _thread_locals.user = request.user if request.user and request.user.is_authenticated else None
        _thread_locals.ip = self.get_client_ip(request)
        
        response = self.get_response(request)
        
        # Clear context
        if hasattr(_thread_locals, 'user'):
            del _thread_locals.user
        if hasattr(_thread_locals, 'ip'):
            del _thread_locals.ip
            
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')

# Pre-save signal to capture old state before saving
_pre_save_cache = {}

def serialize_model_instance(instance):
    """Safely converts a model instance to a dict representation for JSON logging."""
    try:
        data = model_to_dict(instance)
        # Ensure values are JSON serializable
        return json.loads(json.dumps(data, cls=DjangoJSONEncoder))
    except Exception:
        return {}

@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    # Avoid logging the AuditLog model itself to prevent infinite loops
    if sender.__name__ == 'AuditLog':
        return
        
    if instance.pk:
        try:
            # Fetch fresh from database to get the pre-modified state
            old_instance = sender.objects.get(pk=instance.pk)
            _pre_save_cache[id(instance)] = serialize_model_instance(old_instance)
        except Exception:
            pass

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
        
    user = get_current_user()
    ip = get_current_ip()
    
    # Only log if an operator user is authenticated (to avoid cron job noise) or log as system
    action = 'CREATE' if created else 'UPDATE'
    
    old_val = None
    if not created:
        old_val = _pre_save_cache.pop(id(instance), None)
        
    new_val = serialize_model_instance(instance)
    
    # Save the log
    from .models import AuditLog
    from django.db import connection
    try:
        # Check if the auditlog table exists before doing query to prevent breaking atomic block
        if 'core_auditlog' in connection.introspection.table_names():
            AuditLog.objects.create(
                user=user,
                action=action,
                model_name=sender.__name__,
                object_id=str(instance.pk),
                ip_address=ip,
                old_value=old_val,
                new_value=new_val
            )
    except Exception:
        pass

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if sender.__name__ == 'AuditLog':
        return
        
    user = get_current_user()
    ip = get_current_ip()
    
    old_val = serialize_model_instance(instance)
    
    from .models import AuditLog
    from django.db import connection
    try:
        if 'core_auditlog' in connection.introspection.table_names():
            AuditLog.objects.create(
                user=user,
                action='DELETE',
                model_name=sender.__name__,
                object_id=str(instance.pk),
                ip_address=ip,
                old_value=old_val,
                new_value=None
            )
    except Exception:
        pass
