from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DesignationViewSet, EmployeeViewSet, EmployeeDocumentViewSet

router = DefaultRouter()
router.register('departments', DepartmentViewSet, basename='department')
router.register('designations', DesignationViewSet, basename='designation')
router.register('profiles', EmployeeViewSet, basename='employee')
router.register('documents', EmployeeDocumentViewSet, basename='document')

urlpatterns = [
    path('api/', include(router.urls)),
]
