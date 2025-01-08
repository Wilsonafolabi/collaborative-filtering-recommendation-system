from django.urls import path
from . import views


urlpatterns = [
    path('song-search/', views.song_search, name='song_search'),
    path('recommend-tracks/', views.recommend_tracks, name='recommend_tracks'),
    path('login/', views.login, name='login'),
    path('callback/', views.callback, name='callback'),
     path('play-song/', views.play_song, name='play_song'),
]

