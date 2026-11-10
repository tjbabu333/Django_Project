
from typing import ClassVar

from rest_framework.permissions import DjangoModelPermissions


class EmployeeModelPermissions(DjangoModelPermissions):

    perms_map: ClassVar[dict[str, list[str]]] = {
        "GET": ["employees.view_employee"],
        "HEAD": ["employees.view_employee"],
        "OPTIONS": ["employees.view_employee"],
        "POST": ["employees.add_employee"],
        "PUT": ["employees.change_employee"],
        "PATCH": ["employees.change_employee"],
        "DELETE": ["employees.delete_employee"],
    }

