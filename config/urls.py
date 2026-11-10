from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from employees import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("employees/", include("employees.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("register/", views.register, name="register"),
    path(
    "api/",
    include("employees.api_urls")
    ),
    path(
        "api/token/",
        TokenObtainPairView.as_view()
    ),

    path(
        "api/token/refresh/",
        TokenRefreshView.as_view()
    ),
]