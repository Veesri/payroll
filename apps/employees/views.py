from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Department, Designation, Employee, EmployeeDocument
from .serializers import (
    DepartmentSerializer, DesignationSerializer, 
    EmployeeSerializer, EmployeeDocumentSerializer
)
from .permissions import IsHROrAdmin, IsEmployeeSelfOrAdmin

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsHROrAdmin]

class DesignationViewSet(viewsets.ModelViewSet):
    queryset = Designation.objects.all()
    serializer_class = DesignationSerializer
    permission_classes = [IsHROrAdmin]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related('user', 'department', 'designation').all()
    serializer_class = EmployeeSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'create', 'destroy']:
            return [IsHROrAdmin()]
        # retrieve, update, partial_update
        return [IsEmployeeSelfOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Employee.objects.none()
        if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
            return self.queryset
        if user.role == 'DeptManager':
            # return employees in departments they manage
            managed_dept_ids = Department.objects.filter(manager_user=user).values_list('id', flat=True)
            return self.queryset.filter(department_id__in=managed_dept_ids)
        # Regular employee can only see their own profile
        return self.queryset.filter(user=user)

class EmployeeDocumentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeDocument.objects.all()
    serializer_class = EmployeeDocumentSerializer

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin']:
            return self.queryset
        # Employees can only see their own documents
        return self.queryset.filter(employee__user=user)

    def create(self, request, *args, **kwargs):
        # Enforce that normal employees can only upload documents for themselves
        user = request.user
        employee_id = request.data.get('employee')
        
        if user.role not in ['HRAdmin', 'SuperAdmin']:
            try:
                employee = Employee.objects.get(id=employee_id)
                if employee.user != user:
                    return Response(
                        {"detail": "You can only upload documents for your own profile."},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except Employee.DoesNotExist:
                return Response(
                    {"detail": "Employee profile not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
                
        return super().create(request, *args, **kwargs)
