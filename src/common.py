# -*- coding: utf-8 -*-
import sys
import os
import spotipy
import spotipy.util as sp_util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException


# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'

################################################################################
# Authentication Functions
################################################################################
def authenticate_client():
    """
    Using credentials from the environment variables, attempt to authenticate with the spotify web API.  If successful,
    create a spotipy instance and return it.
    :return: An authenticated Spotipy instance
    """
    try:
        # Get an auth token for this user
        client_credentials = SpotifyClientCredentials()

        spotify = spotipy.Spotify(client_credentials_manager=client_credentials)
        return spotify
    except SpotifyOauthError as e:
        print('API credentials not set.  Please see README for instructions on setting credentials.')
        sys.exit(1)


def authenticate_user():
    """
    Prompt the user for their username and authenticate them against the Spotify API.
    (NOTE: You will have to paste the URL from your browser back into the terminal)
    :return: (username, spotify) Where username is the user's username and spotify is an authenticated spotify (spotipy) client
    """
    # Prompt the user for their username
    username = input('\nWhat is your Spotify username: ')

    try:
        # Get an auth token for this user
        token = sp_util.prompt_for_user_token(username, scope=scope)

        spotify = spotipy.Spotify(auth=token)
        return username, spotify
    except SpotifyException as e:
        print('API credentials not set.  Please see README for instructions on setting credentials.')
        sys.exit(1)
    except SpotifyOauthError as e:
        redirect_uri = os.environ.get('SPOTIPY_REDIRECT_URI')
        if redirect_uri is not None:
            print("""
    Uh oh! It doesn't look like that URI was registered as a redirect URI for your application.
    Please check to make sure that "{}" is listed as a Redirect URI and then Try again.'
            """.format(redirect_uri))
        else:
            print("""
    Uh oh! It doesn't look like you set a redirect URI for your application.  Please add
    export SPOTIPY_REDIRECT_URI='http://localhost/'
    to your `credentials.sh`, and then add "http://localhost/" as a Redirect URI in your Spotify Application page.
    Once that's done, try again.'""")
        sys.exit(1)

################################################################################
# Fetcher Functions
################################################################################
def fetch_artists(spotify, artists):
    """
    Get a large number of artists by chunking the requests
    """
    batch_size = 50
    batches = range(0, len(artists), batch_size)
    result = []
    for i in batches:
        end = i+batch_size
        print('Fetching artists {} - {}'.format(i, end))
        chunk = spotify.artists(artists[i:end])
        result = result + chunk.get('artists', [])

    return result

def fetch_artist_top_tracks(spotify, artists):
    """
    Get a large number of artists by chunking the requests
    """
    batch_size = 50
    batches = range(0, len(artists), batch_size)
    result = []
    for i in batches:
        end = i+batch_size
        print('Fetching artists {} - {}'.format(i, end))
        chunk = spotify.artists(artists[i:end])
        result = result + chunk.get('artists', [])

    return result