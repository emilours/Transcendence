from django.db import models

class Score(models.Model):
	user = models.CharField(max_length=100)
	score = models.IntegerField()
	date = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.user} - {self.score}"
