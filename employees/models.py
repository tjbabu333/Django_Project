from django.db import models


# Department Model
class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# Employee Model
class Employee(models.Model):
    name = models.CharField(max_length=100)

    email = models.EmailField(unique=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        related_name="employees"
    )

    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    designation = models.CharField(max_length=100)

    joining_date = models.DateField()

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
