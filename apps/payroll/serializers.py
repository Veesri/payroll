from rest_framework import serializers
from .models import PayrollPeriod, PayrollAdjustment, Holiday, Payroll
from employees.serializers import EmployeeSerializer

class PayrollPeriodSerializer(serializers.ModelSerializer):
    locked_by_name = serializers.CharField(source='locked_by.get_full_name', read_only=True)

    class Meta:
        model = PayrollPeriod
        fields = '__all__'

class PayrollAdjustmentSerializer(serializers.ModelSerializer):
    employee_code = serializers.CharField(source='employee.employee_code', read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)

    class Meta:
        model = PayrollAdjustment
        fields = '__all__'

class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'

class PayrollSerializer(serializers.ModelSerializer):
    employee_details = EmployeeSerializer(source='employee', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)

    class Meta:
        model = Payroll
        fields = '__all__'
