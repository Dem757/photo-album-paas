from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Photo

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['name', 'image']
