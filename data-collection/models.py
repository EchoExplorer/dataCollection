from django.db import models

class CrashLocation(models.Model):
	x = models.IntegerField(max_length=3)
	y = models.IntegerField(max_length=3)
	detail = models.CharField(max_length=300)

class GameLevel(models.Model):
	level = models.IntegerField(max_length=3)
	numSteps = models.IntegerField(max_length=5)
	numCrashes = models.IntegerField(max_length=5)
	echoFileNames = models.CharField(max_length=2000, default='')
	numEchoes = models.IntegerField(max_length=4)  #Total number of echoes played in a game level
	crashLocs = models.ManyToManyField(CrashLocation)
	timeElapsed = models.IntegerField(max_length=4)
	score = models.IntegerField(max_length=6)

class UserGamePerformance(models.Model):
	name = models.CharField(max_length=200, default='user')
	games = models.ManyToManyField(GameLevel)