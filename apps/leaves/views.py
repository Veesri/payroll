from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import date
from .models import LeaveType, LeaveBalance, Leave
from .serializers import LeaveTypeSerializer, LeaveBalanceSerializer, LeaveSerializer
from employees.models import Employee
from employees.permissions import IsManagerOrAdmin, IsHROrAdmin

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [IsHROrAdmin]

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
            return self.queryset
        if user.role == 'DeptManager':
            return self.queryset.filter(employee__department__manager_user=user)
        # Regular employee
        return self.queryset.filter(employee__user=user)

class LeaveViewSet(viewsets.ModelViewSet):
    queryset = Leave.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role in ['HRAdmin', 'SuperAdmin', 'PayrollOfficer']:
            return self.queryset
        if user.role == 'DeptManager':
            return self.queryset.filter(employee__department__manager_user=user)
        # Regular employee
        return self.queryset.filter(employee__user=user)

    def create(self, request, *args, **kwargs):
        user = request.user
        # Find employee
        try:
            employee = user.employee_profile
        except Employee.DoesNotExist:
            return Response({"detail": "User does not have an employee profile."}, status=status.HTTP_400_BAD_REQUEST)
        
        leave_type_id = request.data.get('leave_type')
        start_date_str = request.data.get('start_date')
        end_date_str = request.data.get('end_date')
        
        try:
            leave_type = LeaveType.objects.get(id=leave_type_id)
        except LeaveType.DoesNotExist:
            return Response({"detail": "Invalid leave type."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse dates
        try:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        except (ValueError, TypeError):
            return Response({"detail": "Invalid start_date or end_date format."}, status=status.HTTP_400_BAD_REQUEST)

        if start_date > end_date:
            return Response({"detail": "Start date cannot be after end date."}, status=status.HTTP_400_BAD_REQUEST)

        duration = (end_date - start_date).days + 1
        year = start_date.year

        # Get leave balance for this employee, type, and year
        try:
            balance = LeaveBalance.objects.get(employee=employee, leave_type=leave_type, year=year)
        except LeaveBalance.DoesNotExist:
            return Response({"detail": f"No leave balance allocated for {leave_type.name} in {year}."}, status=status.HTTP_400_BAD_REQUEST)

        if balance.remaining_days < duration:
            return Response({"detail": f"Insufficient leave balance. Remaining: {balance.remaining_days}, Requested: {duration}"}, status=status.HTTP_400_BAD_REQUEST)

        # Create the Leave request
        leave = Leave(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            reason=request.data.get('reason', '')
        )
        leave.save()
        serializer = self.get_serializer(leave)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='approve-manager', permission_classes=[IsManagerOrAdmin])
    def approve_manager(self, request, pk=None):
        leave = self.get_object()
        if leave.status != 'Pending':
            return Response({"detail": "Leave request is already processed."}, status=status.HTTP_400_BAD_REQUEST)
        
        leave.manager_approved_by = request.user
        leave.manager_approval_date = timezone.now()
        leave.save()
        
        serializer = self.get_serializer(leave)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve-hr', permission_classes=[IsHROrAdmin])
    def approve_hr(self, request, pk=None):
        leave = self.get_object()
        if leave.status != 'Pending':
            return Response({"detail": "Leave request is already processed."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if manager has approved it (optional check, or direct override if HR approves)
        # We will require manager approval unless HR overrides
        leave.hr_approved_by = request.user
        leave.hr_approval_date = timezone.now()
        leave.status = 'Approved'
        leave.save()

        # Deduct balance
        year = leave.start_date.year
        try:
            balance = LeaveBalance.objects.get(employee=leave.employee, leave_type=leave.leave_type, year=year)
            balance.used_days += leave.duration_days
            balance.save()
        except LeaveBalance.DoesNotExist:
            # Create a balance record dynamically if missing, though it should exist
            LeaveBalance.objects.create(
                employee=leave.employee,
                leave_type=leave.leave_type,
                year=year,
                allocated_days=leave.leave_type.max_days_per_year,
                used_days=leave.duration_days
            )

        serializer = self.get_serializer(leave)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='reject', permission_classes=[IsManagerOrAdmin])
    def reject(self, request, pk=None):
        leave = self.get_object()
        if leave.status != 'Pending':
            return Response({"detail": "Leave request is already processed."}, status=status.HTTP_400_BAD_REQUEST)
        
        leave.status = 'Rejected'
        # Record who rejected it
        if request.user.role in ['HRAdmin', 'SuperAdmin']:
            leave.hr_approved_by = request.user
            leave.hr_approval_date = timezone.now()
        else:
            leave.manager_approved_by = request.user
            leave.manager_approval_date = timezone.now()
            
        leave.save()
        serializer = self.get_serializer(leave)
        return Response(serializer.data)
