from rest_framework import serializers
from .models import Attendance, AttendanceCorrection
from employees.serializers import EmployeeSerializer

class AttendanceSerializer(serializers.ModelSerializer):
    employee_details = EmployeeSerializer(source='employee', read_only=True)
    
    class Meta:
        model = Attendance
        fields = '__all__'
        read_only_fields = ['status', 'total_hours', 'is_late', 'qr_verified']

class AttendanceCorrectionSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source='attendance.employee.employee_code', read_only=True)
    employee_name = serializers.CharField(source='attendance.employee.user.get_full_name', read_only=True)
    date = serializers.DateField(source='attendance.date', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.get_full_name', read_only=True)

    class Meta:
        model = AttendanceCorrection
        fields = '__all__'
        read_only_fields = ['status', 'reviewed_by', 'reviewed_at']
