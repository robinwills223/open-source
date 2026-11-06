from django.urls import path
from . import views

app_name = "records"

urlpatterns = [
    path("", views.record_list, name="record_list"),
    path("new/", views.record_create, name="record_create"),
    path("<int:pk>/", views.record_detail, name="record_detail"),
    path("<int:pk>/edit/", views.record_update, name="record_update"),
    path("<int:pk>/delete/", views.record_delete, name="record_delete"),
    path("export/", views.record_export_csv, name="record_export_csv"),
]

