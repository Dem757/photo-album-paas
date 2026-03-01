from django.db import models
from django.contrib.auth.models import User

class Photo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Tulajdonos
    name = models.CharField(max_length=40) # Max 40 karakter kikötés
    image = models.ImageField(upload_to='photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True) # Automatikus dátum

    def __str__(self):
        return f"{self.name} ({self.uploaded_at.strftime('%Y-%m-%d %H:%M')})"
