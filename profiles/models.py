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
