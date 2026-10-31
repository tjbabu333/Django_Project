from django.contrib import admin
from django.urls import path, include
from employees import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("employees/", include("employees.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
]