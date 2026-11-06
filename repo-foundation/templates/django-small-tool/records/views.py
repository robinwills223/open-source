"""Views for records tracker with strict user ownership isolation and formula-safe CSV export."""
import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import RecordForm
from .models import Record


def sanitize_csv_cell(value: object) -> str:
    """Protect against spreadsheet formula injection (CSV injection).

    Prefixes cells starting with =, +, -, @, tab, or carriage return with a single quote.
    """
    s = str(value) if value is not None else ""
    if s and s[0] in ("=", "+", "-", "@", "\t", "\r"):
        return f"'{s}"
    return s


@login_required
def record_list(request):
    """List records belonging strictly to the logged-in user, with optional status filter."""
    queryset = Record.objects.filter(user=request.user)
    status_filter = request.GET.get("status")
    valid_statuses = [choice[0] for choice in Record.STATUS_CHOICES]
    if status_filter in valid_statuses:
        queryset = queryset.filter(status=status_filter)

    return render(
        request,
        "records/record_list.html",
        {
            "records": queryset,
            "status_filter": status_filter,
            "status_choices": Record.STATUS_CHOICES,
        },
    )


@login_required
def record_detail(request, pk):
    """View details of a single record owned by the user (returns 404 for other users' records)."""
    record = get_object_or_404(Record, pk=pk, user=request.user)
    return render(request, "records/record_detail.html", {"record": record})


@login_required
def record_create(request):
    """Create a new record assigned to the logged-in user."""
    if request.method == "POST":
        form = RecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.user = request.user
            record.save()
            return redirect("records:record_detail", pk=record.pk)
    else:
        form = RecordForm()
    return render(request, "records/record_form.html", {"form": form, "action": "Create"})


@login_required
def record_update(request, pk):
    """Edit an existing record owned by the user (returns 404 for other users' records)."""
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if request.method == "POST":
        form = RecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            return redirect("records:record_detail", pk=record.pk)
    else:
        form = RecordForm(instance=record)
    return render(request, "records/record_form.html", {"form": form, "action": "Edit", "record": record})


@login_required
def record_delete(request, pk):
    """Delete a record owned by the user (returns 404 for other users' records)."""
    record = get_object_or_404(Record, pk=pk, user=request.user)
    if request.method == "POST":
        record.delete()
        return redirect("records:record_list")
    return render(request, "records/record_confirm_delete.html", {"record": record})


@login_required
def record_export_csv(request):
    """Export the logged-in user's records to CSV with formula injection sanitization."""
    records = Record.objects.filter(user=request.user).order_by("-created_at")

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="my_records.csv"'

    writer = csv.writer(response)
    writer.writerow(["ID", "Title", "Status", "Notes", "Created At", "Updated At"])

    for r in records:
        writer.writerow(
            [
                r.id,
                sanitize_csv_cell(r.title),
                sanitize_csv_cell(r.status),
                sanitize_csv_cell(r.notes),
                r.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                r.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    return response

