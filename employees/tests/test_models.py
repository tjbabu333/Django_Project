from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from employees.models import Department, Employee


class EmployeeModelTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT")
        self.employee = Employee.objects.create(
            name="Test Employee",
            email="model.test@example.com",
            department=self.department,
            designation="Developer",
            salary=Decimal("45000.00"),
            joining_date=date(2026, 11, 6),
            is_active=True,
        )

    def test_employee_is_linked_to_department(self):
        self.assertEqual(self.employee.department.name, "IT")

    def test_employee_fields_are_saved(self):
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.email, "model.test@example.com")
        self.assertEqual(self.employee.salary, Decimal("45000.00"))
        self.assertTrue(self.employee.is_active)

    def test_negative_salary_fails_model_validation(self):
        # Requires MinValueValidator(Decimal("0.00")) on Employee.salary.
        self.employee.salary = Decimal("-1.00")
        with self.assertRaises(ValidationError):
            self.employee.full_clean()

    def test_invalid_email_fails_model_validation(self):
        self.employee.email = "not-an-email"
        with self.assertRaises(ValidationError):
            self.employee.full_clean()

    def test_duplicate_employee_email_is_rejected(self):
        # Requires unique=True on Employee.email.
        duplicate = Employee(
            name="Another Employee",
            email=self.employee.email,
            department=self.department,
            designation="Tester",
            salary=Decimal("30000.00"),
            joining_date=date(2026, 11, 6),
        )
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_duplicate_department_name_is_rejected(self):
        # Requires unique=True on Department.name.
        with self.assertRaises(IntegrityError), transaction.atomic():
            Department.objects.create(name="IT")
