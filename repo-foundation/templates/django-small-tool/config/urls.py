"""URL routing configuration for small-tool."""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("records/", include("records.urls", namespace="records")),
    path("", RedirectView.as_view(url="/records/", permanent=False)),
]

