from django.conf import settings
from django.db import models


class JobPost(models.Model):
    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full-time'
        PART_TIME = 'PART_TIME', 'Part-time'
        INTERN    = 'INTERN', 'Intern'
        CONTRACT  = 'CONTRACT', 'Contract'

    class RemoteType(models.TextChoices):
        ONSITE = 'ONSITE', 'On-site'
        HYBRID = 'HYBRID', 'Hybrid'
        REMOTE = 'REMOTE', 'Remote'

    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='job_posts',
    )

    title = models.CharField(max_length=200)
    description = models.TextField()

    company_name = models.CharField(max_length=200, blank=True)

    employment_type = models.CharField(
        max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME
    )
    remote_type = models.CharField(
        max_length=20, choices=RemoteType.choices, default=RemoteType.ONSITE
    )

    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    visa_sponsorship = models.BooleanField(default=False)

    location_text = models.CharField(max_length=200, blank=True)
    location_lat = models.FloatField(blank=True, null=True)
    location_lng = models.FloatField(blank=True, null=True)

    is_active = models.BooleanField(default=True)  # moderation + “closed job”
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'created_at']),
            models.Index(fields=['remote_type', 'is_active']),
            models.Index(fields=['visa_sponsorship', 'is_active']),
        ]

    def __str__(self) -> str:
        return f'{self.title} ({self.recruiter.username})'


# Written by ChatGPT [$$ - 104]
class JobSkill(models.Model):
    '''
    Keep MVP simple: string skills attached to a job.
    Later you can normalize to a Skill table if you want.
    '''
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=64)

    class Meta:
        unique_together = [('job', 'name')]
        indexes = [models.Index(fields=['name'])]

    def __str__(self) -> str:
        return f'{self.job_id}: {self.name}'


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED    = 'APPLIED', 'Applied'
        REVIEW     = 'REVIEW', 'In Review'
        INTERVIEW  = 'INTERVIEW', 'Interview'
        OFFER      = 'OFFER', 'Offer'
        CLOSED     = 'CLOSED', 'Closed'

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='applications',
    )

    note = models.TextField(blank=True)  # “tailored note”
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('job', 'applicant')]
        indexes = [
            models.Index(fields=['job', 'status']),
            models.Index(fields=['applicant', 'created_at']),
        ]

    def __str__(self) -> str:
        return f'{self.applicant.username} -> {self.job.title} [{self.status}]'


class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='application_status_changes',
    )
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['application', 'created_at'])]
