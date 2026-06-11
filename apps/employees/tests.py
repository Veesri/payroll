from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class RbacPermissionsTestCase(APITestCase):
    def setUp(self):
        # Create user profiles
        self.admin_user = User.objects.create_user(
            username="admin_user", password="password", role="HRAdmin", email="admin@test.com"
        )
        self.emp_user = User.objects.create_user(
            username="emp_user", password="password", role="Employee", email="emp@test.com"
        )
        
    def test_employee_api_permission_denied_for_employee(self):
        # Log in as regular employee
        self.client.login(username="emp_user", password="password")
        
        # Regular employee should not be able to list employee profiles
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_employee_api_permission_allowed_for_admin(self):
        # Log in as HRAdmin
        self.client.login(username="admin_user", password="password")
        
        # HRAdmin should be allowed to view employee profiles
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
