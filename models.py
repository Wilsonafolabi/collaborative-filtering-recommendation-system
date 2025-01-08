from django.db import models

# Create your models here.
from django.db import models
class Song(models.Model):
    track_name = models.CharField(max_length=255)
    artist_name = models.CharField(max_length=255)
    track_id = models.CharField(max_length=300)
    genre = models.CharField(max_length=50)
    danceability = models.FloatField()
    energy = models.FloatField()
    key = models.FloatField()
    loudness = models.FloatField()
    speechiness = models.FloatField()
    acousticness = models.FloatField()
    instrumentalness = models.FloatField()
    liveness = models.FloatField()
    tempo = models.FloatField()

    def __str__(self):
        return f'{self.track_name} by {self.artist_name}'