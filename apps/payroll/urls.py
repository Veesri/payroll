from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayrollPeriodViewSet, PayrollAdjustmentViewSet, HolidayViewSet, PayrollViewSet

router = DefaultRouter()
router.register('periods', PayrollPeriodViewSet, basename='payrollperiod')
router.register('adjustments', PayrollAdjustmentViewSet, basename='payrolladjustment')
router.register('holidays', HolidayViewSet, basename='holiday')
router.register('logs', PayrollViewSet, basename='payroll')

urlpatterns = [
    path('api/', include(router.urls)),
]
