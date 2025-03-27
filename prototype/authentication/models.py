from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = models.CharField(max_length=150, unique=True)
    age = models.PositiveIntegerField()
    location = models.CharField(max_length=200, blank=True, null=True)
    profession = models.CharField(max_length=100)
    education_qualification = models.CharField(max_length=200)
    income = models.DecimalField(max_digits=10, decimal_places=2)
    password = models.CharField(max_length=128)  # In production, use proper password hashing
    
    def __str__(self):
        return self.username

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"