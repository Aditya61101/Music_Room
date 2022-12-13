from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from .credentials import CLIENT_ID, CLIENT_SECRET
from requests import post, put, get

BASE_URL = "https://api.spotify.com/v1/me/"

def get_user_tokens(session_key):
    user_tokens = SpotifyToken.objects.filter(user=session_key)
    if user_tokens.exists():  # same as len(user_tokens)
        return user_tokens[0]
    else:
        return None

def update_create_user_tokens(session_key, access_token, refresh_token, token_type, expires_in):
    tokens = get_user_tokens(session_key)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token',
                    "refresh_token", "expires_in", "token_type"])
    else:
        tokens = SpotifyToken(user=session_key, access_token=access_token,
                              token_type=token_type, expires_in=expires_in, refresh_token=refresh_token)
        tokens.save()

def is_spotify_auth(session_key):
    tokens = get_user_tokens(session_key)
    if tokens:
        date = tokens.expires_in
        if date <= timezone.now():
            refresh_token(session_key)
        return True
    return False

def refresh_token(session_key):
    refresh_token = get_user_tokens(session_key).refresh_token
    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).json()
    access_token = response.get("access_token")
    token_type = response.get("token_type")
    expires_in = response.get("expires_in")
    update_create_user_tokens(session_key, access_token, refresh_token, token_type, expires_in)

def execute_spotify_api_request(session_key, endpoint, is_post=False, is_put=False):
    tokens = get_user_tokens(session_key)
    headers = {"Content-Type":"application/json", "Authorization":"Bearer "+ tokens.access_token}
    if is_post:
        post(BASE_URL + endpoint, headers=headers)
    if is_put:
        put(BASE_URL + endpoint, headers=headers)
    
    response = get(BASE_URL + endpoint, {}, headers=headers)
    try:
        return response.json()
    except:
        return {"message":"Issue with the request"}

def play_song(session_key):
    return execute_spotify_api_request(session_key,"player/play", is_put=True)

def pause_song(session_key):
    return execute_spotify_api_request(session_key,"player/pause", is_put=True)

def skip_song(session_key):
    return execute_spotify_api_request(session_key,"player/next", is_post=True)

