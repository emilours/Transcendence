from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class CustomUser(AbstractBaseUser):
	email = models.EmailField(unique=True)
	first_name = models.CharField(max_length=150)
	last_name = models.CharField(max_length=150)

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	def __str__(self):
		return self.email
