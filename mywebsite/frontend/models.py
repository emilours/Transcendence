from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission

class User(AbstractUser):
	email = models.EmailField(unique=True)
	score = models.IntegerField(default=0)
	games_played = models.IntegerField(default=0)

	# Add related_name to groups and user_permissions fields
	groups = models.ManyToManyField(
		Group,
		related_name='frontend_users',  # Updated related_name
		blank=True,
		help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
		verbose_name='groups',
	)
	user_permissions = models.ManyToManyField(
		Permission,
		related_name='frontend_users_permissions',  # Updated related_name
		blank=True,
		help_text='Specific permissions for this user.',
		verbose_name='user permissions',
	)

	def __str__(self):
		return self.username
