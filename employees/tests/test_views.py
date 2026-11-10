from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from employees.models import Department, Employee


class EmployeeHTMLAndSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.it = Department.objects.create(name="IT")
        cls.hr = Department.objects.create(name="HR")
        cls.viewer = get_user_model().objects.create_user(
            username="view_test_user", password="TestPass!123456"
        )
        cls.viewer.user_permissions.add(
            Permission.objects.get(codename="view_employee", content_type__app_label="employees")
        )
        Employee.objects.create(
            name="Sudhir", email="sudhir.test@example.com", department=cls.it,
            designation="Developer", salary=Decimal("50000.00"),
            joining_date=date(2026, 11, 6), is_active=True,
        )
        Employee.objects.create(
            name="Paramesh", email="paramesh.test@example.com", department=cls.hr,
            designation="Analyst", salary=Decimal("40000.00"),
            joining_date=date(2026, 11, 6), is_active=True,
        )

    def setUp(self):
        self.client.force_login(self.viewer)

    def test_employee_list_loads_departments(self):
        response = self.client.get(reverse("employee_list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_list.html")
        self.assertIn("departments", response.context)
        self.assertCountEqual(
            list(response.context["departments"].values_list("name", flat=True)),
            ["IT", "HR"],
        )

    def test_search_api_is_case_insensitive(self):
        response = self.client.get(reverse("employee_search_api"), {"q": "sUdHiR"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)
        self.assertEqual(response.json()["employees"][0]["name"], "Sudhir")

    def test_search_api_filters_by_department(self):
        response = self.client.get(
            reverse("employee_search_api"), {"department": self.hr.pk}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)
        self.assertEqual(response.json()["employees"][0]["name"], "Paramesh")

    def test_search_api_returns_empty_result(self):
        response = self.client.get(reverse("employee_search_api"), {"q": "xyz987"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["employees"], [])
        self.assertEqual(response.json()["total_count"], 0)

    def test_search_api_rejects_invalid_department(self):
        response = self.client.get(
            reverse("employee_search_api"), {"department": "not-a-number"}
        )
        self.assertEqual(response.status_code, 400)

    def test_search_api_handles_invalid_page(self):
        response = self.client.get(reverse("employee_search_api"), {"page": "abc"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["page"], 1)

    def test_search_api_paginates_after_five_records(self):
        for number in range(4):
            Employee.objects.create(
                name=f"Extra {number}", email=f"extra{number}@example.com",
                department=self.it, designation="Tester", salary=Decimal("1000.00"),
                joining_date=date(2026, 11, 6), is_active=True,
            )
        response = self.client.get(reverse("employee_search_api"), {"page": 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 6)
        self.assertEqual(len(response.json()["employees"]), 1)

    def test_logged_out_user_cannot_access_ajax_search(self):
        self.client.logout()
        response = self.client.get(reverse("employee_search_api"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

