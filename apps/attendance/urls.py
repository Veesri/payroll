from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceViewSet, AttendanceCorrectionViewSet

router = DefaultRouter()
router.register('logs', AttendanceViewSet, basename='attendance')
router.register('corrections', AttendanceCorrectionViewSet, basename='correction')

urlpatterns = [
    path('api/', include(router.urls)),
]
