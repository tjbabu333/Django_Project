"""JWT authentication and model-level authorization regression tests."""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APITestCase

from employees.models import Department, Employee


class EmployeePermissionTests(APITestCase):
    LIST_URL = "/api/employees/"
    TOKEN_URL = "/api/token/"
    REFRESH_URL = "/api/token/refresh/"

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="IT")
        cls.admin = get_user_model().objects.create_superuser(
            username="permission_admin_test", email="permission.admin@example.com",
            password="TestPass!123456",
        )
        cls.restricted = get_user_model().objects.create_user(
            username="permission_employee_test", password="TestPass!123456",
        )
        cls.restricted.user_permissions.add(
            Permission.objects.get(codename="view_employee", content_type__app_label="employees")
        )
        cls.employee = Employee.objects.create(
            name="Permission Test Employee", email="permission.target@example.com",
            department=cls.department, designation="Tester",
            salary=Decimal("45000.00"), joining_date=date(2026, 11, 6),
            is_active=True,
        )

    def get_access_token(self, username):
        response = self.client.post(
            self.TOKEN_URL,
            {"username": username, "password": "TestPass!123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        return response.data["access"]

    def test_token_pair_generation(self):
        response = self.client.post(
            self.TOKEN_URL,
            {"username": "permission_admin_test", "password": "TestPass!123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token_returns_new_access_token(self):
        pair = self.client.post(
            self.TOKEN_URL,
            {"username": "permission_admin_test", "password": "TestPass!123456"},
            format="json",
        )
        self.assertEqual(pair.status_code, status.HTTP_200_OK)
        response = self.client.post(
            self.REFRESH_URL, {"refresh": pair.data["refresh"]}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertIn("access", response.data)

    def test_missing_token_is_rejected(self):
        self.client.credentials()
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid-token")
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_cannot_be_used_as_access_token(self):
        pair = self.client.post(
            self.TOKEN_URL,
            {"username": "permission_admin_test", "password": "TestPass!123456"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {pair.data['refresh']}")
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_employee_without_delete_permission_gets_403(self):
        token = self.get_access_token("permission_employee_test")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.delete(f"{self.LIST_URL}{self.employee.pk}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.assertTrue(Employee.objects.filter(pk=self.employee.pk).exists())

    def test_employee_without_change_permission_cannot_patch_salary(self):
        token = self.get_access_token("permission_employee_test")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.patch(
            f"{self.LIST_URL}{self.employee.pk}/",
            {"salary": "999999.00"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.salary, Decimal("45000.00"))

    def test_admin_can_access_employee_api(self):
        token = self.get_access_token("permission_admin_test")
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
