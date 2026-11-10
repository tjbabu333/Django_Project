
from asyncio.log import logger

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import (
    login_required,
    permission_required,
)
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from .forms import EmployeeForm, RegisterForm
from .models import Department, Employee

# ==========================================
# HOME DASHBOARD
# ==========================================

@login_required
def home(request):

    context = {
        "total_employees": Employee.objects.count(),

        "active_employees": Employee.objects.filter(
            is_active=True
        ).count(),

        "total_departments": Department.objects.count(),

        "recent_employees": Employee.objects.order_by(
            "-joining_date"
        )[:5],
    }

    return render(
        request,
        "employees/home.html",
        context
    )


# ==========================================
# EMPLOYEE LIST
# ==========================================

@login_required
@permission_required(
    "employees.view_employee",
    raise_exception=True
)
def employee_list(request):

    # Get search input
    query = request.GET.get("q", "").strip()

    # Get selected department
    department_id = request.GET.get(
        "department", ""
    ).strip()

    # Retrieve employees
    employees = Employee.objects.select_related(
        "department"
    ).all()

    # Apply search filter
    if query:
        employees = employees.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(department__name__icontains=query)
            | Q(designation__icontains=query)
        )

    # Apply department filter
    if department_id:
        if department_id.isdecimal():
            employees = employees.filter(
                department_id=int(department_id)
            )
        else:
            employees = employees.none()

    # Order employees
    employees = employees.order_by("id")

    # Retrieve ALL departments
    departments = Department.objects.all().order_by(
        "name"
    )

    # Pagination
    paginator = Paginator(employees, 5)

    page_number = request.GET.get("page", 1)

    page_obj = paginator.get_page(page_number)

    # Single context dictionary
    context = {
        "employees": page_obj.object_list,
        "departments": departments,
        "page_obj": page_obj,
        "query": query,
        "selected_department": department_id,
    }

    return render(
        request,
        "employees/employee_list.html",
        context
    )


# ==========================================
# EMPLOYEE DETAILS
# ==========================================

@login_required
@permission_required(
    "employees.view_employee",
    raise_exception=True
)
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


# ==========================================
# CREATE EMPLOYEE
# ==========================================

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


# ==========================================
# UPDATE EMPLOYEE
# ==========================================

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

    # Admins can update employees.
    # Managers with change_employee permission
    # can also update employees.
    # Add record-level restrictions here if
    # Managers may edit only certain employees.

    if request.method == "POST":

        form = EmployeeForm(
            request.POST,
            instance=employee
        )

        if form.is_valid():
            form.save()

            logger.info(
               "Employee %s updated by user %s",
                employee.id,
                request.user.pk
            )
            messages.success(
                request,
                "Employee updated successfully."
            )

            return redirect(
                "employee_detail",
                employee_id=employee.id
            )

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


# ==========================================
# DELETE EMPLOYEE
# ==========================================

@login_required
@permission_required(
    "employees.delete_employee",
    raise_exception=True
)
def employee_delete(request, employee_id):

    # Admin-only delete
    if not request.user.is_superuser:
        raise PermissionDenied

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


# ==========================================
# USER REGISTRATION
# ==========================================

def register(request):

    if request.method == "POST":

        form = RegisterForm(
            request.POST
        )

        if form.is_valid():

            user = form.save()

            login(request, user)

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


# ==========================================
# AJAX EMPLOYEE SEARCH API
# ==========================================

@login_required
@permission_required(
    "employees.view_employee",
    raise_exception=True
)
def employee_search_api(request):

    # Read search parameters
    query = request.GET.get(
        "q", ""
    ).strip()

    department_id = request.GET.get(
        "department", ""
    ).strip()

    page_number = request.GET.get(
        "page", "1"
    )

    # Validate department
    if department_id and not department_id.isdecimal():

        return JsonResponse(
            {
                "error": "Invalid department ID."
            },
            status=400
        )

    # Get employee records
    employees = Employee.objects.select_related(
        "department"
    ).all()

    # Search by multiple fields
    if query:
        employees = employees.filter(
            Q(name__icontains=query)
            | Q(email__icontains=query)
            | Q(designation__icontains=query)
            | Q(department__name__icontains=query)
        )

    # Department filtering
    if department_id:
        employees = employees.filter(
            department_id=int(department_id)
        )

    # Order results
    employees = employees.order_by("id")

    # Pagination
    paginator = Paginator(employees, 5)

    page_obj = paginator.get_page(
        page_number
    )

    # Convert employees to JSON
    employee_data = []

    for employee in page_obj:

        employee_data.append({
            "id": employee.id,
            "name": employee.name,
            "email": employee.email,
            "designation": employee.designation,
            "department": employee.department.name,
            "salary": str(employee.salary)
        })

    return JsonResponse({
        "employees": employee_data,
        "page": page_obj.number,
        "num_pages": paginator.num_pages,
        "has_next": page_obj.has_next(),
        "has_previous": page_obj.has_previous(),
        "total_count": paginator.count
    })


