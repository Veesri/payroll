from rest_framework import permissions

class IsHROrAdmin(permissions.BasePermission):
    """Allows access only to HRAdmin and SuperAdmin roles."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['HRAdmin', 'SuperAdmin']

class IsPayrollOrAdmin(permissions.BasePermission):
    """Allows access to PayrollOfficer, HRAdmin, and SuperAdmin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['PayrollOfficer', 'HRAdmin', 'SuperAdmin']

class IsManagerOrAdmin(permissions.BasePermission):
    """Allows access to DeptManager, HRAdmin, and SuperAdmin."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['DeptManager', 'HRAdmin', 'SuperAdmin']

class IsEmployeeSelfOrAdmin(permissions.BasePermission):
    """Allows employee access to their own data or HR/Admin access."""
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        if request.user.role in ['HRAdmin', 'SuperAdmin']:
            return True
        # Check if obj is Employee or User or related
        if hasattr(obj, 'user'):
            return obj.user == request.user
        return obj == request.user
