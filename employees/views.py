from django.contrib import messages 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required , permission_required
from .models import Department, Employee
from django.contrib.auth import login
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from .forms import RegisterForm

from .forms import EmployeeForm

@login_required
def home(request):
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    total_departments = Department.objects.count()
    recent_employees = Employee.objects.order_by("-joining_date")[:5]

    context = {
         "total_employees": 
             Employee.objects.count(),

         "active_employees":
                Employee.objects.filter(
                    is_active=True
                ).count(),
    
         "total_departments":  
                Department.objects.count(),

         "recent_employees":
                Employee.objects.order_by(
                    "-joining_date"
                )[:5],
    }

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "total_departments": total_departments,
        "recent_employees": recent_employees,
    }
    return render(
        request,
        "employees/home.html",
        context
    )

   
@login_required
def employee_list(request):
    employees = Employee.objects.all()

    return render(
        request,
        "employees/employee_list.html",
        {
            "employees": employees
        }
    )

@login_required
def employee_detail(request, employee_id):

    employee = get_object_or_404(
        Employee.objects.select_related(
            "department"
        ),
        id=employee_id
    )

    return render(
        request,
        "employees/employee_detail.html",
        {
            "employee": employee
        }
    )

@login_required
@permission_required( 
    "employees.add_employee", 
    raise_exception=True
)

def employee_create(request):

    if request.method == "POST":

        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Employee added successfully."
            )

            return redirect("employee_list")

    else:
        form = EmployeeForm()

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Add Employee"
        }
    )

@login_required
@permission_required(
    "employees.change_employee",
    raise_exception=True
)
def employee_update(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Employee updated successfully."
            )

            return redirect(
                "employee_detail",
                employee_id=employee.id
            )

    if not request.user.is_superuser:
         raise PermissionDenied

    else:

        form = EmployeeForm(
            instance=employee
        )

    return render(
        request,
        "employees/employee_form.html",
        {
            "form": form,
            "title": "Update Employee"
        }
    )

@login_required
@permission_required(
    "employees.delete_employee",
    raise_exception=True
)
def employee_delete(request, employee_id):

    employee = get_object_or_404(
        Employee,
        id=employee_id
    )

    if request.method == "POST":

        employee.delete()

        messages.success(
            request,
            "Employee deleted successfully."
        )

        return redirect("employee_list")

    return render(
        request,
        "employees/employee_confirm_delete.html",
        {
            "employee": employee
        }
    )

def register(request):

    if request.method == "POST":

        form = RegisterForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(
                request,
                user
            )

            messages.success(
                request,
                "Registration successful."
            )

            return redirect("home")

    else:

        form = RegisterForm()

    return render(
        request,
        "employees/register.html",
        {
            "form": form
        }
    )

@login_required
def employee_list(request):
    query = request.GET.get("q", "").strip()

    employees = Employee.objects.select_related(
        "department"
    )

    if query:
        employees = employees.filter(
            Q(name__icontains=query)
            |Q(email__icontains=query)
            |Q(department__name__icontains=query)
            |Q(designation__icontains=query)
        )

    return render(
        request,
        "employees/employee_list.html",
        {
            "employees": employees,
            "query": query,
        }
    )

