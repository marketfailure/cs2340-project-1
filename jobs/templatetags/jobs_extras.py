from django import template
from jobs.utils import is_recruiter

register = template.Library()

@register.simple_tag
def user_is_recruiter(user):
    return is_recruiter(user)
