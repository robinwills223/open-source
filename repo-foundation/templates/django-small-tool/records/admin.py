from django.contrib import admin
from .models import Record


@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "status", "updated_at", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "notes", "user__username")

