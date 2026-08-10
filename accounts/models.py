from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE )
    profile_picture = models.ImageField(upload_to="profile_picture/", blank= True, null= True)
    bio = models.TextField(blank= True)

    def __str__(self):
        return self.user.username

    
