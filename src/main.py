import sys
import os
import math
import spotipy
import spotipy.util as sp_util
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOauthError
from spotipy.client import SpotifyException
import json
import matplotlib.pyplot as plt
import numpy as np

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'

feature_keys = [
  'acousticness',
  'danceability',
  'instrumentalness',
  'liveness',
  'speechiness',
  'valence'
]

################################################################################
# Main Demo Function
################################################################################

def main():
    """
    Our main function that will get run when the program executes
    """
    print_header('Vector Histogram Jawn', length=50)


    if not os.path.isfile('tracks.json') or not os.path.isfile('features.json'):
        username, spotipy = authenticate_user()

        tracks = get_library(spotipy)

        features = get_audio_features(spotipy, tracks)

        with open('tracks.json', 'w') as out:
            json.dump(tracks, out)

        with open('features.json', 'w') as out:
            json.dump(features, out)
    else:
        with open('tracks.json') as infile:
            tracks = json.load(infile)

        with open('features.json') as infile:
            features = json.load(infile)

    feature_vectors = features.values()

    # Print tracks with low acousticness values
    # for i, vector in enumerate(feature_vectors):
    #     if vector[0] <= 0.05:
    #         track = tracks[i]
    #         print(track_string(track))


    plt.figure(1)
    for i, key in enumerate(feature_keys):
        vector_values = [vec[i] for vec in feature_vectors]

        cleaned_vector_values = chop_extremes(vector_values)

        print('Outliers: {}'.format((len(vector_values) - len(cleaned_vector_values))))

        plt.subplot(3, 2, i+1)
        plt.hist(vector_values, bins=20, color='#3191ea')
        # plt.hist(cleaned_vector_values, bins=20, color='#8cee76')
        plt.title(key.capitalize())
        plt.xlabel('Value')
        plt.ylabel('Frequency')

    plt.tight_layout()
    plt.show()

def chop_extremes(data, m=0.01):
    tail_length = math.floor(len(data) * m)
    return data[tail_length:(-1 * tail_length)]


def reject_outliers(data, m = 2.0):
    iqr = np.subtract(*np.percentile(data, [75, 25]))
    med = np.median(data)
    max_diff = m * iqr
    return [d for d in data if abs(d-med) < max_diff]


################################################################################
# Convenience Functions
################################################################################

def print_header(message, length=30):
    """
    Given a message, print it with a buncha stars all header-like
    :param message: The message you want to print
    :param length: The number of stars you want to surround it
    """
    print('\n' + ('*' * length))
    print(message)
    print('*' * length)


def track_string(track):
    """
    Given a track, return a string describing the track:
    Track Name - Artist1, Artist2, etc...
    :param track:
    :return: A string describing the track
    """
    track_name = track.get('name')
    artist_names = ', '.join([artist.get('name') for artist in track.get('artists', [])])
    return '{} - {}'.format(track_name, artist_names)


def print_audio_features_for_track(track, track_features):
    """
    Given a track and a features response, print out the desired audio features for that track
    :param track:
    :param track_features:
    :return:
    """
    desired_features = [
        'tempo',
        'time_signature',
        'key',
        'loudness',
        'energy',
        'danceability',
        'acousticness',
        'instrumentalness',
        'liveness',
        'speechiness',
    ]

    print('\n  {}'.format(track_string(track)))
    for feature in desired_features:
        # Pull out the value of the feature from the features
        feature_value = track_features.get(feature)

        # If this feature is the key, convert it to a readable pitch
        if feature == 'key':
            feature_value = translate_key_to_pitch(feature_value)

        # Print the feature value
        print('    {}: {}'.format(feature, feature_value))


def choose_tracks(tracks):
    """
    Given a list of tracks, list them on the console and let the user choose a
    selection of them.
    :return: A list of selected track objects
    """
    for i, track in enumerate(tracks):
        print('  {}) {}'.format(i + 1, track_string(track)))

    # Choose some tracks
    track_choices = input('\nChoose some tracks (e.g 1,4,5,6,10): ')

    # Turn the input into a list of integers
    try:
        track_choice_indexes = [int(choice.strip()) for choice in track_choices.split(',')]
    except ValueError as e:
        print('Error: Invalid input.')
        return []

    # Grab the tracks from our track list and return them
    selected_tracks = [tracks[index - 1] for index in track_choice_indexes]
    return selected_tracks


def get_audio_features(spotify, tracks):
    """
    Given a list of tracks get the audio features for those tracks and return them in a map of trackId->Features
    :param spotify: An authenticated Spotipy instance
    :param tracks: A list of track dictionaries
    """
    if not tracks:
        print('No tracks provided.')
        return

    # Build a map of id->track so we can get the full track info later
    track_ids = [track.get('id') for track in tracks]

    features = {}
    limit = 100
    current = 0
    num_tracks = len(track_ids)

    while current < num_tracks:
        upper = current + limit if current + limit < num_tracks else num_tracks

        # Request the audio features for the chosen tracks (limited to 50)
        tracks_features = spotify.audio_features(tracks=track_ids[current:upper])
        for track_features in tracks_features:
            track_id = track_features.get('id')
            features_array = [track_features.get(key) for key in feature_keys]
            features[track_id] = features_array

        current = upper

    return features


def translate_key_to_pitch(key):
    """
    Given a Key value in Pitch Class Notation, map the key to its actual pitch string
    https://en.wikipedia.org/wiki/Pitch_class
    :param key: The integer key
    :return: The translated Pitch Class string
    """
    pitches = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return pitches[key]


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
# Demo Functions
################################################################################

def search_track():
    """
    This demo function will allow the user to search a song title and pick the song from a list in order to fetch
    the audio features/analysis of it
    """
    keep_searching = True
    selected_track = None

    # Initialize Spotipy
    spotify = authenticate_client()

    # We want to make sure the search is correct
    while keep_searching:
        search_term = input('\nWhat song would you like to search: ')

        # Search spotify
        results = spotify.search(search_term)
        tracks = results.get('tracks', {}).get('items', [])

        if len(tracks) == 0:
            print_header('No results found for "{}"'.format(search_term))
        else:
            # Print the tracks
            print_header('Search results for "{}"'.format(search_term))
            for i, track in enumerate(tracks):
                print('  {}) {}'.format(i + 1, track_string(track)))

        # Prompt the user for a track number, "s", or "c"
        track_choice = input('\nChoose a track #, "s" to search again, or "c" to cancel: ')
        try:
            # Convert the input into an int and set the selected track
            track_index = int(track_choice) - 1
            selected_track = tracks[track_index]
            keep_searching = False
        except (ValueError, IndexError):
            # We didn't get a number.  If the user didn't say 'retry', then exit.
            if track_choice != 's':
                # Either invalid input or cancel
                if track_choice != 'c':
                    print('Error: Invalid input.')
                keep_searching = False

    # Quit if we don't have a selected track
    if selected_track is None:
        return

    # Request the features for this track from the spotify API
    get_audio_features(spotify, [selected_track])


def list_playlists():
    """
    This function will get all of a user's playlists and allow them to choose songs that they want audio features
    for.
    """
    # Prompt for a username
    username = input('\nWhat is your Spotify username: ')

    # Initialize Spotipy
    spotify = authenticate_client()

    # Get all the playlists for this user
    playlists = []
    total = 1
    # The API paginates the results, so we need to iterate
    while len(playlists) < total:
        playlists_response = spotify.user_playlists(username, offset=len(playlists))
        playlists.extend(playlists_response.get('items', []))
        total = playlists_response.get('total')

    # Remove any playlists that we don't own
    playlists = [playlist for playlist in playlists if playlist.get('owner', {}).get('id') == username]

    # List out all of the playlists
    print_header('Your Playlists')
    for i, playlist in enumerate(playlists):
        print('  {}) {} - {}'.format(i + 1, playlist.get('name'), playlist.get('uri')))

    # Choose a playlist
    playlist_choice = int(input('\nChoose a playlist: '))
    playlist = playlists[playlist_choice - 1]
    playlist_owner = playlist.get('owner', {}).get('id')

    # Get the playlist tracks
    tracks = []
    total = 1
    # The API paginates the results, so we need to keep fetching until we have all of the items
    while len(tracks) < total:
        tracks_response = spotify.user_playlist_tracks(playlist_owner, playlist.get('id'), offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

    # Pull out the actual track objects since they're nested weird
    tracks = [track.get('track') for track in tracks]

    # Print out our tracks along with the list of artists for each
    print_header('Tracks in "{}"'.format(playlist.get('name')))

    # Let em choose the tracks
    selected_tracks = choose_tracks(tracks)

    # Print the audio features :)
    get_audio_features(spotify, selected_tracks)


def get_library(spotify):
    """
    Get all of the tracks from a user's library and return them in a list
    :param spotify: A *user_authenticated* spotipy instance
    """
    # Get all the playlists for this user
    tracks = []
    total = 1
    first_fetch = True
    # The API paginates the results, so we need to iterate
    while len(tracks) < total:
        tracks_response = spotify.current_user_saved_tracks(offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

        # Some users have a LOT of tracks.  Warn them that this might take a second
        if first_fetch and total > 150:
            print('\nYou have a lot of tracks saved - {} to be exact!\nGive us a second while we fetch them...'.format(
                total))
            first_fetch = False

    # Pull out the actual track objects since they're nested weird
    tracks = [track.get('track') for track in tracks]

    return tracks

def list_library():
    """
    This function will get all songs saved in a user's library and allow them to choose which tracks to get audio
    features for.
    """
    username, spotify = authenticate_user()

    # Get all the playlists for this user
    tracks = []
    total = 1
    first_fetch = True
    # The API paginates the results, so we need to iterate
    while len(tracks) < total:
        tracks_response = spotify.current_user_saved_tracks(offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

        # Some users have a LOT of tracks.  Warn them that this might take a second
        if first_fetch and total > 150:
            print('\nYou have a lot of tracks saved - {} to be exact!\nGive us a second while we fetch them...'.format(
                total))
            first_fetch = False

    # Pull out the actual track objects since they're nested weird
    tracks = [track.get('track') for track in tracks]

    # Let em choose the tracks
    selected_tracks = choose_tracks(tracks)

    # Print the audio features :)
    get_audio_features(spotify, selected_tracks)


if __name__ == '__main__':
    main()
