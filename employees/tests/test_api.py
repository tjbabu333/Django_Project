"""REST API regression tests. Requires DRF, Simple JWT and /api/employees/ routes."""
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from employees.models import Department, Employee


class EmployeeAPITests(APITestCase):
    LIST_URL = "/api/employees/"

    @classmethod
    def setUpTestData(cls):
        cls.department = Department.objects.create(name="IT")
        cls.admin = get_user_model().objects.create_superuser(
            username="api_admin_test", email="api.admin@example.com",
            password="TestPass!123456",
        )
        cls.employee = Employee.objects.create(
            name="Existing API Employee", email="existing.api@example.com",
            department=cls.department, designation="Developer",
            salary=Decimal("45000.00"), joining_date=date(2026, 11, 6),
            is_active=True,
        )

    def setUp(self):
        # Authenticate with a real JWT (not force_authenticate).
        token = RefreshToken.for_user(self.admin).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def detail_url(self, employee_id):
        return f"{self.LIST_URL}{employee_id}/"

    def employee_data(self, **overrides):
        data = {
            "name": "New API Employee",
            "email": "new.api@example.com",
            "department": self.department.pk,
            "designation": "Tester",
            "salary": "30000.00",
            "joining_date": "2026-11-06",
            "is_active": True,
        }
        data.update(overrides)
        return data

    def test_get_employee_list(self):
        response = self.client.get(self.LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_employee_detail(self):
        response = self.client.get(self.detail_url(self.employee.pk))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], self.employee.pk)

    def test_post_creates_employee(self):
        response = self.client.post(
            self.LIST_URL, self.employee_data(), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(Employee.objects.filter(email="new.api@example.com").exists())

    def test_put_replaces_employee_fields(self):
        response = self.client.put(
            self.detail_url(self.employee.pk),
            self.employee_data(email=self.employee.email, designation="Senior Developer"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.designation, "Senior Developer")

    def test_patch_changes_only_selected_field(self):
        original_name = self.employee.name
        response = self.client.patch(
            self.detail_url(self.employee.pk), {"salary": "60000.00"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.salary, Decimal("60000.00"))
        self.assertEqual(self.employee.name, original_name)

    def test_delete_removes_employee(self):
        response = self.client.delete(self.detail_url(self.employee.pk))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Employee.objects.filter(pk=self.employee.pk).exists())

    def test_invalid_email_is_rejected(self):
        response = self.client.post(
            self.LIST_URL, self.employee_data(email="not-an-email"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("email", response.data)

    def test_negative_salary_is_rejected(self):
        response = self.client.post(
            self.LIST_URL, self.employee_data(salary="-5000.00"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("salary", response.data)

    def test_duplicate_email_is_rejected(self):
        response = self.client.post(
            self.LIST_URL, self.employee_data(email=self.employee.email), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("email", response.data)

    def test_missing_department_is_rejected(self):
        payload = self.employee_data()
        del payload["department"]
        response = self.client.post(self.LIST_URL, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertIn("department", response.data)

    def test_unknown_employee_id_returns_404(self):
        response = self.client.get(self.detail_url(999999))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_malformed_json_returns_400(self):
        response = self.client.generic(
            "POST", self.LIST_URL,
            data=b'{"name": "Incomplete",',
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
