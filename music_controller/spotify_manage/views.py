from django.shortcuts import redirect
from .credentials import REDIRECT_URI, CLIENT_ID, CLIENT_SECRET
from rest_framework.views import APIView
from requests import Request, post
from rest_framework.response import Response
from rest_framework import status
from .util import *
from api.models import Room
from .models import Vote

# Create your views here.


class AuthURL(APIView):
    def get(self, request, format=None):
        scopes = "user-read-playback-state user-modify-playback-state user-read-currently-playing"
        # .prepare().url generates a string that we will use as a url in frontend
        url = Request("GET", "https://accounts.spotify.com/authorize", params={
            "scopes": scopes,
            "response_type": 'code',
            "redirect_uri": REDIRECT_URI,
            "client_id": CLIENT_ID
        }).prepare().url
        return Response({"url": url}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get("code")
    error = request.GET.get("error")
    response = post("https://accounts.spotify.com/api/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }).json()
    access_token = response.get("access_token")
    token_type = response.get("token_type")
    refresh_token = response.get("refresh_token")
    expires_in = response.get("expires_in")
    error = response.get("error")

    if not request.session.exists(request.session.session_key):
        request.session.create()
    session_key = request.session.session_key
    update_create_user_tokens(
        session_key, access_token, refresh_token, token_type, expires_in)
    return redirect("frontend:")


class IsAuth(APIView):
    def get(self, request, format=None):
        is_auth = is_spotify_auth(self.request.session.session_key)
        return Response({"isAuth": is_auth}, status=status.HTTP_200_OK)


class CurrentSongView(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get("room_code")
        filtered_room = Room.objects.filter(code=room_code)
        if len(filtered_room) > 0:
            room = filtered_room[0]
            host = room.host
        # end point to access currently playing song of the user
            endpoint = "player/currently-playing"
            response = execute_spotify_api_request(host, endpoint)
            print(response)
            if "error" in response or "item" not in response:
                return Response(response,  status=response["error"]["status"])
            item = response.get("item")
            duration = item.get("duration_ms")
            progress = response.get("progress_ms")
            album_cover = item.get("album").get("images")[0].get("url")
            is_playing = response.get("is_playing")
            song_id = item.get("id")
            artist_str = ""
            for i, artist in enumerate(item.get("artists")):
                if i > 0:
                    artist_str += ", "
                name = artist.get("name")
                artist_str += name
            curr_votes = len(Vote.objects.filter(room=room, song_id=song_id))
            song = {
                "title": item.get("name"),
                "duration": duration,
                "time": progress,
                "img_url": album_cover,
                "artist": artist_str,
                "is_playing": is_playing,
                "votes": curr_votes,
                "votes_required": room.votes_to_skip,
                "id": song_id
            }
            self.update_room_song(room, song_id)
            return Response(song, status=status.HTTP_200_OK)
        return Response({}, status=status.HTTP_404_NOT_FOUND)

    # function to update the song in the room currently playing
    def update_room_song(self, room, song_id):
        curr_song = room.curr_song
        if curr_song != song_id:
            room.curr_song = song_id
            room.save(update_fields=["curr_song"])
            # if the song has been skipped then all the votes related to it should be deleted
            votes = Vote.objects.filter(room=room).delete()


class PauseSongView(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get("room_code")
        filtered_room = Room.objects.filter(code=room_code)
        if len(filtered_room) > 0:
            room = filtered_room[0]
            if room.guest_can_pause or self.request.session.session_key == room.host:
                pause_song(room.host)
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "Your are not allowed to pause the song"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)


class PlaySongView(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get("room_code")
        filtered_room = Room.objects.filter(code=room_code)
        if len(filtered_room) > 0:
            room = filtered_room[0]
            if room.guest_can_pause or self.request.session.session_key == room.host:
                play_song(room.host)
                return Response({}, status=status.HTTP_204_NO_CONTENT)
            return Response({"message": "Your are not allowed to pause the song"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Not found"}, status=status.HTTP_404_NOT_FOUND)


class SkipSongView(APIView):
    def post(self, request, format=None):
        room_code = self.request.session.get("room_code")
        filtered_room = Room.objects.filter(code=room_code)
        if filtered_room.exists():
            room = filtered_room[0]
            curr_votes = Vote.objects.filter(room=room, song_id=room.curr_song)
            votes_needed = room.votes_to_skip
            if self.request.session.session_key == room.host or len(curr_votes)+1 >= votes_needed:
                curr_votes.delete()
                skip_song(room.host)
            # if the conditions doesn't satisfy then we just add the vote of the current user
            else:
                vote = Vote(user=self.request.session.session_key,
                            room=room, song_id=room.curr_song)
                vote.save()
            return Response({}, status=status.HTTP_204_NO_CONTENT)
