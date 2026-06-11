from django.urls import path
from .views import (
    dashboard_view, employees_list_view, attendance_dashboard_view,
    leaves_list_view, payroll_process_view, payslips_list_view, audit_logs_view
)

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('employees/', employees_list_view, name='employees_list'),
    path('attendance/', attendance_dashboard_view, name='attendance_dashboard'),
    path('leaves/', leaves_list_view, name='leaves_list'),
    path('payroll/', payroll_process_view, name='payroll_process'),
    path('payslips/', payslips_list_view, name='payslips_list'),
    path('audit-logs/', audit_logs_view, name='audit_logs'),
]
