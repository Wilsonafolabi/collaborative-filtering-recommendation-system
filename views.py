from django.shortcuts import render, get_object_or_404, redirect
from .models import Song
from django.http import JsonResponse
from .forms import SongSelectionForm
from .utils import load_knn_model
import pandas as pd
from sklearn.preprocessing import StandardScaler
import random
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
from django.views.decorators.csrf import csrf_exempt

print("Loading KNN model and scaler...") 
knn = load_knn_model()
scaler = StandardScaler()
print("KNN model and scaler loaded.")  
from django.shortcuts import redirect
from spotipy.oauth2 import SpotifyOAuth
import requests
import base64
from django.conf import settings
import json



CLIENT_ID = '42a20510bdea4aca92cb36940691f364'
CLIENT_SECRET = '39bf39d9e42e417b8a4e558a9038bea5'
REDIRECT_URI = 'http://127.0.0.1:8000/callback/' 
SCOPE = 'user-read-email user-read-private user-modify-playback-state user-read-playback-position user-library-read streaming user-read-playback-state'


sp_oauth = SpotifyOAuth(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI, scope=SCOPE)
print("Spotify OAuth setup completed.")

def login(request):
    """Redirects to Spotify authorization URL."""
    print("Login view called.")
    auth_url = sp_oauth.get_authorize_url()
    print(f"Generated Spotify authorization URL: {auth_url}")
    print("Login view completed.")
    return redirect(auth_url)

def get_access_token(code):
    """Exchanges authorization code for access token."""
    url = 'https://accounts.spotify.com/api/token'
    
    client_creds = f"{CLIENT_ID}:{CLIENT_SECRET}"
    client_creds_b64 = base64.b64encode(client_creds.encode())
    
    headers = {
        'Authorization': f'Basic {client_creds_b64.decode()}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
    }
    
    response = requests.post(url, headers=headers, data=data)
    print(f"Response from token endpoint: {response.status_code}")
    
    if response.status_code == 200:
        token_info = response.json()
        print(f"Token info received: {token_info}")
        return token_info
    else:
        print(f"Failed to get access token: {response.text}")
        return None

def callback(request):
    """Handles Spotify's callback with authorization code."""
    print("Callback view called.")
    code = request.GET.get('code')
    print(f"Received authorization code: {code}")
    
    if code:
        token_info = get_access_token(code)
        print(f"Access token retrieved: {token_info}")
        
        if token_info:
            request.session['token_info'] = token_info
            print("Token info saved to session.")
        else:
            print("Failed to retrieve token info.")
    else:
        print("No authorization code received.")

    return redirect('recommend_tracks')


@csrf_exempt
def play_song(request):
    """Starts playback of a specific song on Spotify."""
    print("Play song view called.")

   
    token_info = request.session.get('token_info')
    print(f"Token info: {token_info}")

    if not token_info:
        print("No token info found, unauthorized request.")
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    token = token_info.get('access_token')
    
    try:
        data = json.loads(request.body)
        print(f"Request data: {data}")
    except json.JSONDecodeError:
        print("Failed to decode JSON from request body.")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    device_id = data.get('device_id')
    track_id = data.get('track_id')
    
    if not device_id or not track_id:
        print("Missing device_id or track_id in request.")
        return JsonResponse({'error': 'Bad Request: device_id and track_id are required'}, status=400)

    print(f"Preparing to play song with track ID: {track_id} on device ID: {device_id}")

    url = f"https://api.spotify.com/v1/me/player/play?device_id={device_id}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        "uris": [f"spotify:track:{track_id}"]
    }
    
    try:
        response = requests.put(url, headers=headers, json=data)
        print(f"Sent play request to Spotify, response status: {response.status_code}")
        if response.status_code != 200:
            print(f"Error response from Spotify: {response.text}")
        return JsonResponse({'status': response.status_code, 'response': response.json()})
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return JsonResponse({'error': 'Request failed'}, status=500)


def song_search(request):
    """Searches for songs based on query and returns results."""
    print("Song search view called.") 
    query = request.GET.get('q', '')
    print(f"Received search query: {query}")  
    songs = Song.objects.filter(track_name__icontains=query)[:10]
    results = [{'id': song.id, 'text': song.track_name} for song in songs]
    print(f"Found songs: {[song.track_name for song in songs]}")
    print("Song search view completed.") 
    return JsonResponse({'results': results})
def recommend_tracks(request):
    """Generates song recommendations based on selected song."""
    print("Recommend tracks view called.") 
    
    token_info = request.session.get('token_info', {})
    print(f"Token info from session: {token_info}")
    token = token_info.get('access_token', '')
    print(f"Access token retrieved: {token}")

    if request.method == 'POST':
        print("POST request received.") 
        form = SongSelectionForm(request.POST)
        print(f"Form data: {request.POST}")
        if form.is_valid():
            print("Form is valid.")
            selected_song = form.cleaned_data['song']
            print(f"Selected song: {selected_song}") 
            artist_name = selected_song.artist_name
            genre = selected_song.genre

            excluded_ids = [selected_song.id]
            print("Fetching same artist songs...") 
            same_artist_songs = Song.objects.filter(artist_name=artist_name).exclude(id__in=excluded_ids)[:10]
            excluded_ids.extend([song.id for song in same_artist_songs])
            print(f"Same artist songs: {[song.track_name for song in same_artist_songs]}")
            print("Fetching same genre songs...") 
            same_genre_songs = list(Song.objects.filter(genre=genre).exclude(id__in=excluded_ids).distinct())
            random.shuffle(same_genre_songs)
            same_genre_songs = same_genre_songs[:10]  
            excluded_ids.extend([song.id for song in same_genre_songs])
            print(f"Same genre songs: {[song.track_name for song in same_genre_songs]}") 

            feature_cols = ['danceability', 'energy', 'key', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'tempo']
            all_songs = Song.objects.all()
            song_data = pd.DataFrame(list(all_songs.values(*feature_cols)))
            print("Fitting scaler on song data...") 
            scaler.fit(song_data[feature_cols])
            X = song_data[feature_cols]
            X_scaled = scaler.transform(X)
            print("Scaler fitted on song data.")  

            selected_features = pd.DataFrame([selected_song.__dict__], columns=feature_cols)
            selected_features_scaled = scaler.transform(selected_features[feature_cols])
            print("Performing KNN to get recommendations...")  
            distances, indices = knn.kneighbors(selected_features_scaled, n_neighbors=4)
            knn_recommendations = all_songs.filter(id__in=[all_songs[int(idx)].id for idx in indices[0][1:]])
            print(f"KNN Recommendations: {[song.track_name for song in knn_recommendations]}") 

            context = {
                'form': form,
                'same_artist_songs': same_artist_songs,
                'same_genre_songs': same_genre_songs,
                'knn_recommendations': knn_recommendations,
                'token': token  
            }
            print("Rendering recommendations template...") 
            print("Recommend tracks view completed.")  
            return render(request, 'recommendations.html', context)
        else:
            print(f"Form is invalid\nForm errors: {form.errors}")  
            print("Rendering form with errors...") 
            print("Recommend tracks view completed with form errors.") 
            return render(request, 'recommendations.html', {'form': form})
    else:
        print("GET request received.") 
        form = SongSelectionForm()
        print("Rendering recommendations form...") 
        print("Recommend tracks view completed.") 
        
        return render(request, 'recommendations.html', {'form': form, 'token': token})
