from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render, redirect

from .forms import ProfileEditForm

def profile_view(request, username: str):
    User = get_user_model()
    try:
        user = User.objects.select_related('profile').get(username=username)
    except User.DoesNotExist:
        raise Http404('User not found')

    return render(request, 'view.html', {'puser': user})

@login_required
def profile_edit_me(request):
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_view', username=request.user.username)
        return render(request, 'edit.html', {'form': form})

    form = ProfileEditForm(instance=profile)
    return render(request, 'edit.html', {'form': form})
