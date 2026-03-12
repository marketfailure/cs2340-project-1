from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import get_user_model
from profiles.models import Profile

from .utils import recruiter_only, job_seeker_only, is_recruiter
from .forms import JobPostForm, JobSearchForm, ApplicationForm, ApplicationStatusForm
from .models import JobPost, JobSkill, Application, ApplicationStatusHistory


def job_list(request):
    form = JobSearchForm(request.GET or None)

    qs = JobPost.objects.filter(is_active=True).select_related('recruiter').prefetch_related('skills')

    search_lat = None
    search_lng = None
    search_radius = None

    if form.is_valid():
        q = form.cleaned_data.get('q') or ''
        skill = form.cleaned_data.get('skill') or ''
        remote_type = form.cleaned_data.get('remote_type') or ''
        visa = form.cleaned_data.get('visa_sponsorship')
        salary_min = form.cleaned_data.get('salary_min')
        salary_max = form.cleaned_data.get('salary_max')

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(company_name__icontains=q)
            )

        if skill:
            qs = qs.filter(skills__name__icontains=skill)

        if remote_type:
            qs = qs.filter(remote_type=remote_type)

        if visa in ('1', '0'):
            qs = qs.filter(visa_sponsorship=(visa == '1'))

        if salary_min is not None:
            qs = qs.filter(Q(salary_min__lte=salary_min) | Q(salary_min__isnull=True))

        if salary_max is not None:
            qs = qs.filter(Q(salary_max__gte=salary_max) | Q(salary_max__isnull=True))

        qs = qs.distinct()

        lat = form.cleaned_data.get('lat')
        lng = form.cleaned_data.get('lng')
        radius = form.cleaned_data.get('radius_miles')

        search_lat = lat
        search_lng = lng
        search_radius = radius

        if lat is not None and lng is not None and radius is not None:
            import math
            deg_lat = radius / 69.0
            cos_lat = max(0.2, abs(math.cos(math.radians(lat))))
            deg_lng = radius / (69.0 * cos_lat)

            qs = qs.filter(
                location_lat__isnull=False,
                location_lng__isnull=False,
                location_lat__gte=lat - deg_lat,
                location_lat__lte=lat + deg_lat,
                location_lng__gte=lng - deg_lng,
                location_lng__lte=lng + deg_lng,
            )

    qs = qs.order_by('-created_at')

    # Edited with ChatGPT (DB search)
    recommended_jobs = []
    if request.user.is_authenticated and not is_recruiter(request.user):
        user_skills = list(request.user.profile.skills.values_list('name', flat=True))

        if user_skills:
            recommended_jobs = (
                JobPost.objects
                .filter(is_active=True)
                .annotate(
                    match_count=Count(
                        'skills',
                        filter=Q(skills__name__in=user_skills),
                        distinct=True,
                    )
                )
                .filter(match_count__gt=0)
                .select_related('recruiter')
                .prefetch_related('skills')
                .order_by('-match_count', '-created_at')[:5]
            )

    job_markers = [
        {
            'id': j.id,
            'title': j.title,
            'company_name': j.company_name or '',
            'location_text': j.location_text or '',
            'remote_type': j.remote_type or '',
            'lat': j.location_lat,
            'lng': j.location_lng,
        }
        for j in qs
        if j.location_lat is not None and j.location_lng is not None
    ]

    return render(request, 'jobs/list.html', {
        'form': form,
        'jobs': qs,
        'recommended_jobs': recommended_jobs,
        'job_markers': job_markers,
        'search_lat': search_lat,
        'search_lng': search_lng,
        'search_radius': search_radius,
    })

def job_detail(request, job_id: int):
    job = get_object_or_404(
        JobPost.objects.select_related('recruiter').prefetch_related('skills'),
        id=job_id,
    )
    if not job.is_active and not (
        request.user.is_authenticated
        and is_recruiter(request.user)
        and job.recruiter_id == request.user.id
    ):
        raise Http404('Job not found')

    already_applied = False
    if request.user.is_authenticated and not is_recruiter(request.user):
        already_applied = Application.objects.filter(job=job, applicant=request.user).exists()

    return render(request, 'jobs/detail.html', {
        'job': job,
        'already_applied': already_applied,
    })


@login_required
@job_seeker_only
def job_apply(request, job_id: int):
    job = get_object_or_404(JobPost, id=job_id, is_active=True)
    existing = Application.objects.filter(job=job, applicant=request.user).first()
    if existing:
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        form = ApplicationForm(request.POST)
        if form.is_valid():
            app = form.save(commit=False)
            app.job = job
            app.applicant = request.user
            app.status = Application.Status.APPLIED
            app.save()
            return redirect('my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'jobs/apply.html', {'job': job, 'form': form})


@login_required
@job_seeker_only
def my_applications(request):
    apps = (
        Application.objects
        .filter(applicant=request.user)
        .select_related('job', 'job__recruiter')
        .order_by('-created_at')
    )
    return render(request, 'jobs/my_applications.html', {'apps': apps})


@login_required
@recruiter_only
def recruiter_job_new(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()

            JobSkill.objects.filter(job=job).delete()
            for s in form.cleaned_skill_list():
                JobSkill.objects.create(job=job, name=s)

            return redirect('recruiter_job_edit', job_id=job.id)
    else:
        form = JobPostForm(initial={'is_active': True})

    return render(request, 'jobs/recruiter_edit.html', {'form': form, 'job': None})


@login_required
@recruiter_only
def recruiter_job_edit(request, job_id: int):
    job = get_object_or_404(JobPost, id=job_id, recruiter=request.user)

    if request.method == 'POST':
        form = JobPostForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()

            JobSkill.objects.filter(job=job).delete()
            for s in form.cleaned_skill_list():
                JobSkill.objects.create(job=job, name=s)

            return redirect('recruiter_job_edit', job_id=job.id)
    else:
        skills_csv = ', '.join(job.skills.order_by('name').values_list('name', flat=True))
        form = JobPostForm(instance=job, initial={'skills': skills_csv})

    return render(request, 'jobs/recruiter_edit.html', {'form': form, 'job': job})


@login_required
@recruiter_only
def recruiter_pipeline(request, job_id: int):
    job = get_object_or_404(
        JobPost.objects.prefetch_related('skills'),
        id=job_id,
        recruiter=request.user,
    )

    apps = (
        Application.objects
        .filter(job=job)
        .select_related('applicant', 'applicant__profile')
        .order_by('-updated_at')
    )

    buckets = {k: [] for k, _ in Application.Status.choices}
    for a in apps:
        buckets[a.status].append(a)

    applicant_markers = []
    for a in apps:
        profile = getattr(a.applicant, 'profile', None)
        if not profile:
            continue
        if profile.location_lat is None or profile.location_lng is None:
            continue

        if profile.hide_name_from_recruiters:
            applicant_name = a.applicant.username
        elif profile.full_name:
            applicant_name = profile.full_name
        else:
            applicant_name = a.applicant.username

        applicant_markers.append({
            'application_id': a.id,
            'name': applicant_name,
            'username': a.applicant.username,
            'status': a.status,
            'location_text': profile.location_text or '',
            'lat': profile.location_lat,
            'lng': profile.location_lng,
            'profile_url': f'/profiles/{a.applicant.username}/',
        })

    job_skill_names = list(job.skills.values_list('name', flat=True))
    applied_user_ids = list(apps.values_list('applicant_id', flat=True))

    recommended_candidates = []
    if job_skill_names:
        User = get_user_model()

        # DB fetch written by ChatGPT
        recommended_candidates = (
            User.objects
            .filter(profile__skills__name__in=job_skill_names)
            .exclude(id__in=applied_user_ids)
            .exclude(id=request.user.id)
            .exclude(groups__name='recruiters')
            .select_related('profile')
            .prefetch_related(
                'profile__skills',
                'profile__education',
                'profile__work_experience',
                'profile__links',
            )
            .annotate(
                match_count=Count(
                    'profile__skills',
                    filter=Q(profile__skills__name__in=job_skill_names),
                    distinct=True,
                )
            )
            .filter(match_count__gt=0)
            .distinct()
            .order_by('-match_count', 'username')[:8]
        )

    return render(request, 'jobs/pipeline.html', {
        'job': job,
        'buckets': buckets,
        'applicant_markers': applicant_markers,
        'recommended_candidates': recommended_candidates,
    })


@login_required
@recruiter_only
def recruiter_set_status(request, app_id: int):
    app = get_object_or_404(Application.objects.select_related('job'), id=app_id)
    if app.job.recruiter_id != request.user.id:
        raise Http404('Application not found')

    if request.method != 'POST':
        return redirect('recruiter_pipeline', job_id=app.job.id)

    form = ApplicationStatusForm(request.POST)
    if form.is_valid():
        new_status = form.cleaned_data['status']
        old_status = app.status
        if new_status != old_status:
            app.status = new_status
            app.save(update_fields=['status', 'updated_at'])
            ApplicationStatusHistory.objects.create(
                application=app,
                changed_by=request.user,
                old_status=old_status,
                new_status=new_status,
            )

    return redirect('recruiter_pipeline', job_id=app.job.id)

@login_required
@recruiter_only
def recruiter_jobs(request):
    jobs = (
        JobPost.objects
        .filter(recruiter=request.user)
        .order_by('-updated_at')
    )
    return render(request, 'jobs/recruiter_jobs.html', {'jobs': jobs})
