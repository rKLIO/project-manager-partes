from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # Django crée automatiquement un champ id unique pour chaque utilisateur, 
    # donc on peut s'en passer. Cependant, on le laisse pour plus de clarté.
    id = models.AutoField(primary_key=True)
    
    # Additional fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=255)  # Le mot de passe est géré par Django, mais il est explicitement mentionné ici

    # Optional fields
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'
