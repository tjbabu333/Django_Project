from typing import ClassVar

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Employee


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User

        fields = (
            "username",
            "email",
            "password1",
            "password2",
        )


class EmployeeForm(forms.ModelForm):

    def clean_salary(self):
          salary = self.cleaned_data.get("salary")

          if salary is not None and salary <= 0:
               raise forms.ValidationError(
                      "Salary must be greater than zero."
               )

          return salary

    def clean_name(self):
           name = self.cleaned_data.get("name")

           if name and len(name.strip()) < 2:
               raise forms.ValidationError(
                       "Name must contain at least 2 characters."
               )
           return name
    
    class Meta:
        model = Employee

        fields = (
            "name",
            "email",
            "department",
            "salary",
            "designation",
            "joining_date",
            "is_active",
        )

        widgets : ClassVar[dict] = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "department": forms.Select(
                attrs={
                    "class": "form-select"
                }
            ),

            "salary": forms.NumberInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "designation": forms.TextInput(
                attrs={
                    "class": "form-control"
                }
            ),

            "joining_date": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date"
                }
            ),
        }