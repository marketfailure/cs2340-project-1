from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path("<int:job_id>/", views.job_detail, name="job_detail"),
    path("<int:job_id>/apply/", views.job_apply, name="job_apply"),
    path("me/applications/", views.my_applications, name="my_applications"),
    path("recruiter/new/", views.recruiter_job_new, name="recruiter_job_new"),
    path("recruiter/<int:job_id>/edit/", views.recruiter_job_edit, name="recruiter_job_edit"),
    path("recruiter/<int:job_id>/pipeline/", views.recruiter_pipeline, name="recruiter_pipeline"),
    path("recruiter/application/<int:app_id>/status/", views.recruiter_set_status, name="recruiter_set_status"),
    path("recruiter/", views.recruiter_jobs, name="recruiter_jobs"),
]
