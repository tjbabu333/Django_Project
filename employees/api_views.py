from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from .api_permissions import EmployeeModelPermissions
from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    permission_classes = (
        IsAuthenticated,
        EmployeeModelPermissions,
    )

    filter_backends = (
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_fields = (
        "department",
        "is_active",
    )

    search_fields = (
        "name",
        "email",
        "designation",
    )

    ordering_fields = (
        "name",
        "salary",
        "joining_date",
    )

    def get_queryset(self):
        return Employee.objects.select_related(
            "department"
        )