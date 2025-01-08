import os
import django
import pandas as pd

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recommender.settings')
django.setup()

from recommeder_system.models import Song

# Load data
songs = pd.read_csv('song.csv')

# Clear existing entries to avoid duplicates
Song.objects.all().delete()

# Save new entries
for _, row in songs.iterrows():
    song = Song(
        track_name=row['track_name'],
        artist_name=row['artist_name'],
        track_id=row['track_id'],
        danceability=row['danceability'],
        energy=row['energy'],
        key=row['key'],
        loudness=row['loudness'],
        speechiness=row['speechiness'],
        acousticness=row['acousticness'],
        instrumentalness=row['instrumentalness'],
        liveness=row['liveness'],
        tempo=row['tempo'],
        genre=row['genre']
    )
    song.save()

    print(f"Saved: {row['artist_name']} - {row['track_name']} - {row['genre']} - {row['track_id']}")
