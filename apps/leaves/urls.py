from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveTypeViewSet, LeaveBalanceViewSet, LeaveViewSet

router = DefaultRouter()
router.register('types', LeaveTypeViewSet, basename='leavetype')
router.register('balances', LeaveBalanceViewSet, basename='leavebalance')
router.register('requests', LeaveViewSet, basename='leave')

urlpatterns = [
    path('api/', include(router.urls)),
]
