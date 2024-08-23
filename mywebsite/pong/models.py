from django.db import models

# Create your models here.

# created at the end of a game
class Game(models.Model):
    # users are User model
    # user1 = 
    # user2 
    user1Score = models.IntegerField()
    user2Score = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
