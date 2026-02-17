from django import forms
from .models import JobPost, Application

# Written by ChatGPT ($$ - EOF)


class JobPostForm(forms.ModelForm):
    skills = forms.CharField(
        label="Skills (comma-separated)",
        required=False,
        help_text="Example: Python, Django, SQL"
    )

    class Meta:
        model = JobPost
        fields = [
            "title",
            "company_name",
            "description",
            "employment_type",
            "remote_type",
            "salary_min",
            "salary_max",
            "visa_sponsorship",
            "location_text",
            "location_lat",
            "location_lng",
            "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }

    def clean(self):
        cd = super().clean()
        smin = cd.get("salary_min")
        smax = cd.get("salary_max")
        if smin is not None and smin < 0:
            self.add_error("salary_min", "Salary min must be >= 0.")
        if smax is not None and smax < 0:
            self.add_error("salary_max", "Salary max must be >= 0.")
        if smin is not None and smax is not None and smin > smax:
            self.add_error("salary_max", "Salary max must be >= salary min.")
        return cd

    def cleaned_skill_list(self) -> list[str]:
        raw = (self.cleaned_data.get("skills") or "").strip()
        if not raw:
            return []
        parts = [p.strip() for p in raw.split(",")]
        # normalize: drop empties, lowercase for uniqueness but keep original-ish
        out = []
        seen = set()
        for p in parts:
            if not p:
                continue
            key = p.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(p)
        return out


class JobSearchForm(forms.Form):
    q = forms.CharField(label="Search", required=False)
    skill = forms.CharField(label="Skill", required=False)
    remote_type = forms.ChoiceField(
        label="Remote",
        required=False,
        choices=[("", "Any")] + list(JobPost.RemoteType.choices),
    )
    visa_sponsorship = forms.ChoiceField(
        label="Visa",
        required=False,
        choices=[("", "Any"), ("1", "Yes"), ("0", "No")],
    )
    salary_min = forms.IntegerField(label="Min salary", required=False, min_value=0)
    salary_max = forms.IntegerField(label="Max salary", required=False, min_value=0)


    # distance filtering (optional)
    lat = forms.FloatField(required=False)
    lng = forms.FloatField(required=False)
    radius_miles = forms.FloatField(required=False, min_value=0)


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["note"]
        widgets = {"note": forms.Textarea(attrs={"rows": 4})}


class ApplicationStatusForm(forms.Form):
    status = forms.ChoiceField(choices=Application.Status.choices)
