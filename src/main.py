import json
import sys
import spotipy
import spotipy.util as sp_util

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'


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
        'dancibility',
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


def translate_key_to_pitch(key):
    """
    Given a Key value in Pitch Class Notation, map the key to its actual pitch string
    https://en.wikipedia.org/wiki/Pitch_class
    :param key: The integer key
    :return: The translated Pitch Class string
    """
    pitches = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return pitches[key]


def main():
    """
    Our main function that will get run when the program executes
    """
    print_header('Spotify Web API Demo App', length=50)

    # Run our demo function
    retry = True
    while retry:
        print('Would you like to:\n  1.) Search for a song\n  2.) Choose from your playlists')
        program_choice = input('Choice: ')
        if program_choice == '1':
            search_track()
        elif program_choice == '2':
            audio_features_demo()

        # Prompt the user to run again
        retry_input = input('\nRun the program again? (Y/N): ')
        retry = retry_input.lower() == 'y'


def search_track():
    """
    This demo function will allow the user to search a song title and pick the song from a list in order to fetch
    the audio features/analysis of it
    """
    keep_searching = True
    selected_track = None

    # Initialize Spotipy
    username, spotify = authenticate()

    # We want to make sure the search is correct
    while keep_searching:
        search_term = input('\nWhat song would you like to search: ')

        # Search spotify
        results = spotify.search(search_term)
        tracks = results.get('tracks', {}).get('items', [])

        # Print the tracks
        print_header('Search results for "{}"'.format(search_term))
        for i, track in enumerate(tracks):
            print('  {}) {}'.format(i + 1, track_string(track)))

        # Prompt the user for a track number or "retry"
        track_choice = input('\nChoose a track # (or "retry" to search again): ')
        try:
            # Convert the input into an int and set the selected track
            track_index = int(track_choice) - 1
            selected_track = tracks[track_index]
            keep_searching = False
        except ValueError:
            # We didn't get a number.  If the user didn't say 'retry', then exit.
            if track_choice != 'retry':
                print('Invalid input.')
                keep_searching = False

    # Quit if we don't have a selected track
    if selected_track is None:
        return

    # Request the features for this track from the spotify API
    features = spotify.audio_features(selected_track.get('id'))[0]

    # Print the features
    print_header('Audio Features')
    print_audio_features_for_track(selected_track, features)


def audio_features_demo():
    """
    This demo function will get all of a user's playlists and allow them to choose songs that they want audio features
    for.
    """
    # Initialize Spotipy
    username, spotify = authenticate()

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

    # Print out our tracks along with the list of artists for each
    print_header('Tracks in "{}"'.format(playlist.get('name')))
    for i, track in enumerate(tracks):
        track_info = track.get('track')
        print('  {}) {}'.format(i + 1, track_string(track_info)))

    # Choose some tracks
    track_choices = input('\nChoose some tracks (e.g 1,4,5,6,10): ')

    # Turn the input into a list of integers
    track_choice_indexes = [int(choice.strip()) for choice in track_choices.split(',')]

    # Grab the tracks from our track list and build a map of id->track
    selected_tracks = [tracks[index - 1].get('track') for index in track_choice_indexes]
    track_map = {track.get('id'): track for track in selected_tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    tracks_features = spotify.audio_features(tracks=track_map.keys())

    # Iterate through the features and print the track and info
    print_header('Audio Features')
    for track_features in tracks_features:
        # Get the track from the track map
        track_id = track_features.get('id')
        track = track_map.get(track_id)

        # Print out the track info and audio features
        print_audio_features_for_track(track, track_features)


def authenticate():
    """
    Prompt the user for their username and authenticate them against the Spotify API.
    (NOTE: You will have to paste the URL from your browser back into the terminal)
    :return: (username, spotify) Where username is the user's username and spotify is an authenticated spotify (spotipy) client
    """
    # Prompt the user for their username
    username = input('\nWhat is your Spotify username: ')

    try:
        with open('credentials.json') as f:
            credentials = json.load(f)

            # Get an auth token for this user
            token = sp_util.prompt_for_user_token(username,
                                                  client_id=credentials.get('client_id'),
                                                  client_secret=credentials.get('client_secret'),
                                                  redirect_uri=credentials.get('redirect_uri',
                                                                               'http://localhost/'),
                                                  scope=scope)

            spotify = spotipy.Spotify(auth=token)
            return username, spotify
    except IOError as e:
        print('Unable to find/read credentials.json file.  Please see README for instructions on creating this file.')
        sys.exit(1)


if __name__ == '__main__':
    main()
