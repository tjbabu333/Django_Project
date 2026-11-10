from django.urls import path

from . import views

urlpatterns = [
    path("", views.employee_list, name="employee_list"),
    path("add/", views.employee_create, name="employee_create"),
    path("<int:employee_id>/", views.employee_detail, name="employee_detail"),
    path("<int:employee_id>/edit/", views.employee_update, name="employee_update"),
    path("<int:employee_id>/delete/", views.employee_delete, name="employee_delete"),
    path("search-api/", views.employee_search_api, name="employee_search_api"),
]

