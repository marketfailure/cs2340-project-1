from functools import wraps
from django.http import HttpResponseForbidden


def is_recruiter(u) -> bool:
    return u.is_authenticated and u.groups.filter(name='recruiters').exists()


def recruiter_only(view_fn):
    @wraps(view_fn)
    def _wrapped(request, *args, **kwargs):
        if not is_recruiter(request.user):
            return HttpResponseForbidden('Recruiters only.')
        return view_fn(request, *args, **kwargs)
    return _wrapped


def job_seeker_only(view_fn):
    @wraps(view_fn)
    def _wrapped(request, *args, **kwargs):
        if is_recruiter(request.user):
            # TODO: replace with error, im too lazy :(
            return HttpResponseForbidden('Job seekers only.')
        return view_fn(request, *args, **kwargs)
    return _wrapped
