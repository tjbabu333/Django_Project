from datetime import date
from decimal import Decimal

from django.test import TestCase

from employees.forms import EmployeeForm
from employees.models import Department, Employee


class EmployeeFormTests(TestCase):
    def setUp(self):
        self.department = Department.objects.create(name="IT")
        self.valid_data = {
            "name": "Form Test Employee",
            "email": "form.test@example.com",
            "department": self.department.pk,
            "designation": "Developer",
            "salary": "45000.00",
            "joining_date": date(2026, 11, 6).isoformat(),
            "is_active": True,
        }

    def test_valid_employee_form(self):
        form = EmployeeForm(data=self.valid_data)
        self.assertTrue(form.is_valid(), form.errors.as_json())

    def test_invalid_email_is_rejected(self):
        data = {**self.valid_data, "email": "not-an-email"}
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_negative_salary_is_rejected(self):
        # Requires a minimum-value validator on the model or form.
        data = {**self.valid_data, "salary": "-5000.00"}
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("salary", form.errors)

    def test_required_department_is_validated(self):
        data = {**self.valid_data, "department": ""}
        form = EmployeeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("department", form.errors)

    def test_duplicate_email_is_rejected(self):
        # Requires unique=True on Employee.email.
        Employee.objects.create(
            name="Existing", email=self.valid_data["email"],
            department=self.department, designation="Developer",
            salary=Decimal("30000.00"), joining_date=date(2026, 11, 6),
        )
        form = EmployeeForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
