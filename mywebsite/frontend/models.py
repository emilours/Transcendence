from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
	def create_user(self, email, password=None, **extra_fields):
		if not email:
			raise ValueError('The Email field must be set')
		user = self.model(email=self.normalize_email(email), **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

class CustomUser(AbstractBaseUser):
	email = models.EmailField(unique=True)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	objects = CustomUserManager()

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
