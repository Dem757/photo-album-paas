from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Photo
from .forms import PhotoForm, UserRegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import HttpResponse

def photo_list(request):
    sort_by = request.GET.get('sort', '-uploaded_at') # Alapértelmezett: legfrissebb előre
    photos = Photo.objects.all().order_by(sort_by)
    return render(request, 'gallery/photo_list.html', {'photos': photos})

@login_required # Csak belépve engedi
def photo_upload(request):
    if request.method == 'POST':
        form = PhotoForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)
            photo.user = request.user
            photo.save()
            return redirect('photo_list')
    else:
        form = PhotoForm()
    return render(request, 'gallery/photo_upload.html', {'form': form})

@login_required
def photo_delete(request, pk):
    photo = get_object_or_404(Photo, pk=pk, user=request.user) # Csak a sajátját törölheti
    photo.delete()
    return redirect('photo_list')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Fiók létrehozva: {username}! Most már beléphetsz.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'gallery/register.html', {'form': form})


def logout_view(request):
    """Require POST to log out; show confirmation on GET."""
    if request.method == 'POST':
        logout(request)
        return redirect('photo_list')
    return render(request, 'registration/logout_confirm.html')
