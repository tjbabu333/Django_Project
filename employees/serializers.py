from decimal import Decimal

from rest_framework import serializers

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(
        source="department.name",
        read_only=True
    )

    class Meta:
        model = Employee
        fields = (
            "id",
            "name",
            "email",
            "department",
            "department_name",
            "salary",
            "designation",
            "joining_date",
            "is_active",
        )

    def validate_salary(self, value):

            if value < Decimal("0.00"):
                raise serializers.ValidationError(
                     "Salary cannot be negative."
                )

            return value