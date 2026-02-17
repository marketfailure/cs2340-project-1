from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from functools import wraps

from .forms import ProfileEditForm, SkillForm, EducationForm, WorkExperienceForm, AboutLinkForm, RecruiterProfileEditForm
from .models import Skill, Education, WorkExperience, AboutLink

def is_recruiter(u) -> bool:
    return u.is_authenticated and u.groups.filter(name='recruiters').exists()

def job_seeker_only(view_fn):
    @wraps(view_fn)
    def _wrapped(request, *args, **kwargs):
        if request.user.groups.filter(name="recruiters").exists():
            return HttpResponseForbidden("Recruiters cannot edit job seeker sections.")
        return view_fn(request, *args, **kwargs)
    return _wrapped

def profile_view(request, username: str):
    User = get_user_model()
    try:
        user = (
            User.objects
            .select_related('profile')
            .prefetch_related(
                'profile__skills',
                'profile__education',
                'profile__work_experience',
                'profile__links',
            )
            .get(username=username)
        )
    except User.DoesNotExist:
        raise Http404('User not found')

    viewer_is_owner = request.user.is_authenticated and request.user.username == user.username
    viewer_is_recruiter = is_recruiter(request.user)
    target_is_recruiter = is_recruiter(user)

    p = user.profile

    can_show_name = viewer_is_owner or (not viewer_is_recruiter or not p.hide_name_from_recruiters)
    can_show_bio = viewer_is_owner or (not viewer_is_recruiter or not p.hide_bio_from_recruiters)
    can_show_skills = viewer_is_owner or (not viewer_is_recruiter or not p.hide_skills_from_recruiters)
    can_show_education = viewer_is_owner or (not viewer_is_recruiter or not p.hide_education_from_recruiters)
    can_show_work = viewer_is_owner or (not viewer_is_recruiter or not p.hide_work_from_recruiters)
    can_show_links = viewer_is_owner or (not viewer_is_recruiter or not p.hide_links_from_recruiters)

    template = 'views/' + ('view_recruiter.html' if target_is_recruiter else 'view_jobseeker.html')

    return render(request, template, {
        'puser': user,
        'viewer_is_owner': viewer_is_owner,
        'viewer_is_recruiter': viewer_is_recruiter,
        'can_show_name': can_show_name,
        'can_show_bio': can_show_bio,
        'can_show_skills': can_show_skills,
        'can_show_education': can_show_education,
        'can_show_work': can_show_work,
        'can_show_links': can_show_links,
    })

@login_required
def profile_edit_me(request):
    profile = request.user.profile
    recruiter = is_recruiter(request.user)

    FormCls = RecruiterProfileEditForm if recruiter else ProfileEditForm
    template = 'edits/' + ('edit_recruiter.html' if recruiter else 'edit_jobseeker.html')

    if request.method == 'POST':
        form = FormCls(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
        return render(request, template, {'form': form})

    form = FormCls(instance=profile)
    return render(request, template, {'form': form})


@login_required
@job_seeker_only
def skills_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return redirect('skills_edit')
    else:
        form = SkillForm()

    skills = profile.skills.all().order_by('name')
    return render(request, 'edits/skills.html', {'form': form, 'skills': skills})


@login_required
@job_seeker_only
@require_POST
def skill_delete(request, skill_id: int):
    profile = request.user.profile
    Skill.objects.filter(id=skill_id, profile=profile).delete()
    return redirect('skills_edit')


@login_required
@job_seeker_only
def education_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return redirect('education_edit')
    else:
        form = EducationForm()

    education = profile.education.all().order_by('-end_year', '-start_year', 'school')
    return render(request, 'edits/education.html', {'form': form, 'education': education})


@login_required
@job_seeker_only
@require_POST
def education_delete(request, edu_id: int):
    profile = request.user.profile
    Education.objects.filter(id=edu_id, profile=profile).delete()
    return redirect('education_edit')


@login_required
@job_seeker_only
def work_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return redirect('work_edit')
    else:
        form = WorkExperienceForm()

    work = profile.work_experience.all().order_by('-is_current', '-end_date', '-start_date', '-id')
    return render(request, 'edits/work.html', {'form': form, 'work': work})


@login_required
@require_POST
@job_seeker_only
def work_delete(request, work_id: int):
    profile = request.user.profile
    WorkExperience.objects.filter(id=work_id, profile=profile).delete()
    return redirect('work_edit')


@login_required
@job_seeker_only
def links_edit(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = AboutLinkForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.profile = profile
            obj.save()
            return redirect('links_edit')
    else:
        form = AboutLinkForm()

    links = profile.links.all().order_by('label')
    return render(request, 'edits/links.html', {'form': form, 'links': links})


@login_required
@job_seeker_only
@require_POST
def link_delete(request, link_id: int):
    profile = request.user.profile
    AboutLink.objects.filter(id=link_id, profile=profile).delete()
    return redirect('links_edit')
