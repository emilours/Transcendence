from django.contrib.auth.models import User
from django.db import models

# Create your models here.

# created at the end of a game
# class Game(models.Model):
#     # users are User model

#     user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user1', null=True)
#     user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user2', null=True)
#     user1Score = models.IntegerField()
#     user2Score = models.IntegerField()
#     date = models.DateTimeField(auto_now_add=True)
