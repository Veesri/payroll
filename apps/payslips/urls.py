from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayslipViewSet

router = DefaultRouter()
router.register('records', PayslipViewSet, basename='payslip')

urlpatterns = [
    path('api/', include(router.urls)),
]
