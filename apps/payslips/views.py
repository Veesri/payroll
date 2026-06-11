import os
from django.conf import settings
from django.http import HttpResponse
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Payslip
from .serializers import PayslipSerializer
from .services import dispatch_payslip_email, generate_pdf_payslip
from employees.permissions import IsPayrollOrAdmin

class PayslipViewSet(viewsets.ModelViewSet):
    queryset = Payslip.objects.select_related('payroll', 'payroll__employee', 'payroll__period').all()
    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
            return self.queryset
        # Regular employee
        return self.queryset.filter(payroll__employee__user=user)

    @action(detail=True, methods=['get'], url_path='download')
    def download_pdf(self, request, pk=None):
        payslip = self.get_object()
        
        # Check if PDF exists, otherwise generate it
        pdf_path = payslip.pdf_file.path if payslip.pdf_file else None
        if not pdf_path or not os.path.exists(pdf_path):
            pdf_path = generate_pdf_payslip(payslip)
            
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
            
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{payslip.payslip_code}.pdf"'
        return response

    @action(detail=True, methods=['post'], url_path='send-email', permission_classes=[IsPayrollOrAdmin])
    def send_email(self, request, pk=None):
        payslip = self.get_object()
        
        # Check if PDF exists, generate if needed
        pdf_path = payslip.pdf_file.path if payslip.pdf_file else None
        if not pdf_path or not os.path.exists(pdf_path):
            generate_pdf_payslip(payslip)
            
        success = dispatch_payslip_email(payslip)
        if success:
            return Response({"detail": f"Payslip email sent to {payslip.payroll.employee.user.email} successfully."})
        return Response({"detail": "Failed to dispatch email. Verify user email configuration."}, status=status.HTTP_400_BAD_REQUEST)
