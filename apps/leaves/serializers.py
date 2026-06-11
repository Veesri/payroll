from rest_framework import serializers
from .models import LeaveType, LeaveBalance, Leave
from employees.serializers import EmployeeSerializer

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    leave_type_code = serializers.CharField(source='leave_type.code', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)

    class Meta:
        model = LeaveBalance
        fields = '__all__'

class LeaveSerializer(serializers.ModelSerializer):
    employee_details = EmployeeSerializer(source='employee', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    duration = serializers.IntegerField(source='duration_days', read_only=True)
    manager_name = serializers.CharField(source='manager_approved_by.get_full_name', read_only=True)
    hr_name = serializers.CharField(source='hr_approved_by.get_full_name', read_only=True)

    class Meta:
        model = Leave
        fields = '__all__'
        read_only_fields = [
            'status', 
            'manager_approved_by', 'manager_approval_date',
            'hr_approved_by', 'hr_approval_date'
        ]
