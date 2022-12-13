from django.urls import path
from .views import *

urlpatterns = [
    path("get-auth", AuthURL.as_view()),
    path("redirect", spotify_callback),
    path("check-auth", IsAuth.as_view()),
    path("curr-song", CurrentSongView.as_view()),
    path("play-song", PlaySongView.as_view()),
    path("pause-song", PauseSongView.as_view()),
    path("skip-song", SkipSongView.as_view()),
]