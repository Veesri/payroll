from rest_framework import serializers
from .models import Payslip
from payroll.serializers import PayrollSerializer

class PayslipSerializer(serializers.ModelSerializer):
    payroll_details = PayrollSerializer(source='payroll', read_only=True)
    employee_code = serializers.CharField(source='payroll.employee.employee_code', read_only=True)
    employee_name = serializers.CharField(source='payroll.employee.user.get_full_name', read_only=True)
    period_name = serializers.CharField(source='payroll.period.name', read_only=True)
    net_salary = serializers.DecimalField(source='payroll.net_salary', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Payslip
        fields = '__all__'
