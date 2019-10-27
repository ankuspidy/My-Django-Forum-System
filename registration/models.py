from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.png', upload_to='profile_pics')
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    birth_day = models.DateField(null=True, blank=True)
    nickname = models.CharField(max_length=20, unique=True)
    summary = models.CharField(max_length=100, null=True, blank=True)
    social_media = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'