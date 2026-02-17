from django.contrib import admin
from .models import JobPost, JobSkill, Application, ApplicationStatusHistory

# Written by ChatGPT

@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company_name", "remote_type", "visa_sponsorship", "is_active", "created_at", "updated_at")
    list_filter = ("is_active", "remote_type", "visa_sponsorship", "created_at")
    search_fields = ("title", "company_name", "description", "location_text")
    list_editable = ("is_active",)
    ordering = ("-created_at",)

admin.site.register(JobSkill)
admin.site.register(Application)
admin.site.register(ApplicationStatusHistory)
