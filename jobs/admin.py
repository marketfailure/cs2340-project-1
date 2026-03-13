from django.contrib import admin
from django.http import HttpResponse
from django.utils import timezone
import csv

from .models import JobPost, JobSkill, Application, ApplicationStatusHistory

# Written by ChatGPT

def export_as_csv(modeladmin, request, queryset):
    model = modeladmin.model
    meta = model._meta

    response = HttpResponse(content_type="text/csv")
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    response["Content-Disposition"] = (
        f'attachment; filename="{meta.model_name}_{timestamp}.csv"'
    )

    writer = csv.writer(response)

    field_names = [field.name for field in meta.fields]
    writer.writerow(field_names)

    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field)
            row.append("" if value is None else str(value))
        writer.writerow(row)

    return response


export_as_csv.short_description = "Export selected rows to CSV"


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "company_name",
        "remote_type",
        "visa_sponsorship",
        "is_active",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "remote_type", "visa_sponsorship", "created_at")
    search_fields = ("title", "company_name", "description", "location_text")
    list_editable = ("is_active",)
    ordering = ("-created_at",)
    actions = [export_as_csv]


@admin.register(JobSkill)
class JobSkillAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    actions = [export_as_csv]


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(admin.ModelAdmin):
    actions = [export_as_csv]
