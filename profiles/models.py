from django.db import models

from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    bio = models.TextField()

    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'.strip()

    def __str__(self) -> str:
        return f'Profile({self.user.username})'

class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.profile.user.username}: {self.name}'


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=128)
    degree = models.CharField(max_length=128, blank=True)
    field_of_study = models.CharField(max_length=128, blank=True)
    start_year = models.PositiveSmallIntegerField(blank=True, null=True)
    end_year = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.profile.user.username}: {self.school}'


class WorkExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='work_experience')
    company = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    location = models.CharField(max_length=128, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __str__(self):
        return f'{self.profile.user.username}: {self.title} @ {self.company}'


class AboutLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    label = models.CharField(max_length=64)
    url = models.URLField(max_length=300)

    def __str__(self):
        return f'{self.profile.user.username}: {self.label}'
