from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import date
from .models import Attendance, AttendanceCorrection
from .serializers import AttendanceSerializer, AttendanceCorrectionSerializer
from .services import generate_daily_qr_token, verify_qr_token
from employees.models import Employee
from employees.permissions import IsManagerOrAdmin, IsHROrAdmin

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
            return self.queryset
        if user.role == 'DeptManager':
            return self.queryset.filter(employee__department__manager_user=user)
        # Regular employee sees own attendance
        return self.queryset.filter(employee__user=user)

    @action(detail=False, methods=['post'], url_path='check-in')
    def check_in(self, request):
        user = request.user
        # Find employee
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "User does not have an employee profile."}, status=status.HTTP_400_BAD_REQUEST)
        
        today = date.today()
        # Check if already checked in today
        if Attendance.objects.filter(employee=employee, date=today).exists():
            return Response({"detail": "Already checked in today."}, status=status.HTTP_400_BAD_REQUEST)
        
        qr_token = request.data.get('qr_token')
        qr_verified = False
        if qr_token:
            success, msg = verify_qr_token(qr_token)
            if not success:
                return Response({"detail": f"QR verification failed: {msg}"}, status=status.HTTP_400_BAD_REQUEST)
            qr_verified = True

        now = timezone.now()
        attendance = Attendance(
            employee=employee,
            date=today,
            check_in=now,
            qr_verified=qr_verified
        )
        attendance.save()
        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='check-out')
    def check_out(self, request):
        user = request.user
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "User does not have an employee profile."}, status=status.HTTP_400_BAD_REQUEST)
        
        today = date.today()
        # Find today's attendance log
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
        except Attendance.DoesNotExist:
            return Response({"detail": "No check-in record found for today."}, status=status.HTTP_400_BAD_REQUEST)
        
        if attendance.check_out:
            return Response({"detail": "Already checked out today."}, status=status.HTTP_400_BAD_REQUEST)
        
        attendance.check_out = timezone.now()
        attendance.save()
        serializer = self.get_serializer(attendance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='today-status')
    def today_status(self, request):
        user = request.user
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "No profile found."}, status=status.HTTP_404_NOT_FOUND)
        
        today = date.today()
        try:
            attendance = Attendance.objects.get(employee=employee, date=today)
            serializer = self.get_serializer(attendance)
            return Response(serializer.data)
        except Attendance.DoesNotExist:
            return Response({"detail": "Not checked in today", "checked_in": False})

    @action(detail=False, methods=['get'], url_path='qr-token', permission_classes=[IsManagerOrAdmin])
    def get_qr_token(self, request):
        """Generates a secure QR token for displaying on screen/kiosk."""
        token = generate_daily_qr_token()
        return Response({"qr_token": token, "date": str(date.today())})

class AttendanceCorrectionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceCorrection.objects.all()
    serializer_class = AttendanceCorrectionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin']:
            return self.queryset
        if user.role == 'DeptManager':
            return self.queryset.filter(attendance__employee__department__manager_user=user)
        # Employees view their own correction requests
        return self.queryset.filter(attendance__employee__user=user)

    def create(self, request, *args, **kwargs):
        # Allow employee to request correction for their own attendance
        user = request.user
        attendance_id = request.data.get('attendance')
        
        try:
            attendance = Attendance.objects.get(id=attendance_id)
            if attendance.employee.user != user and user.role not in ['HRAdmin', 'SuperAdmin']:
                return Response({"detail": "You can only request corrections for your own attendance logs."}, status=status.HTTP_403_FORBIDDEN)
        except Attendance.DoesNotExist:
            return Response({"detail": "Attendance log not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if a pending correction already exists
        if AttendanceCorrection.objects.filter(attendance=attendance, status='Pending').exists():
            return Response({"detail": "A correction request is already pending for this attendance log."}, status=status.HTTP_400_BAD_REQUEST)
            
        return super().create(request, *args, **kwargs)

    @action(detail=True, methods=['post'], url_path='review', permission_classes=[IsManagerOrAdmin])
    def review(self, request, pk=None):
        correction = self.get_object()
        action_val = request.data.get('action') # 'Approve' or 'Reject'
        
        if action_val not in ['Approve', 'Reject']:
            return Response({"detail": "Invalid review action. Must be 'Approve' or 'Reject'."}, status=status.HTTP_400_BAD_REQUEST)
        
        if correction.status != 'Pending':
            return Response({"detail": "This correction request has already been reviewed."}, status=status.HTTP_400_BAD_REQUEST)
            
        if action_val == 'Approve':
            correction.status = 'Approved'
            # Update the underlying attendance record
            attendance = correction.attendance
            attendance.check_in = correction.requested_check_in
            attendance.check_out = correction.requested_check_out
            attendance.save() # This triggers hours calculation and status updates automatically
        else:
            correction.status = 'Rejected'
            
        correction.reviewed_by = request.user
        correction.reviewed_at = timezone.now()
        correction.save()
        
        serializer = self.get_serializer(correction)
        return Response(serializer.data)
