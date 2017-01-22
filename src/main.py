import json
import sys
import spotipy
import spotipy.util as sp_util

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'


def print_header(message, length=50):
    """
    Given a message, print it with a buncha stars all header-like
    :param message: The message you want to print
    :param length: The number of stars you want to surround it
    """
    print('\n' + ('*' * length))
    print(message)
    print('*' * length)


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
    print_header('Spotify Web API Demo App')

    # Run our demo function
    retry = True
    while retry:
        # Run our demo script
        audio_features_demo()

        # Prompt the user to run again
        retry_input = input('\nRun the program again? (Y/N): ')
        retry = retry_input.lower() == 'y'


def audio_features_demo():
    """
    This demo function will get all of a user's playlists and allow them to choose songs that they want audio features
    for.
    """
    # Prompt the user for their username
    username = input('\nWhat is your Spotify username: ')

    # Initialize Spotipy
    token = get_token(username)
    sp = spotipy.Spotify(auth=token)

    # Get all the playlists for this user
    playlists = []
    total = 1
    # The API paginates the results, so we need to iterate
    while len(playlists) < total:
        playlists_response = sp.user_playlists(username, offset=len(playlists))
        playlists.extend(playlists_response.get('items', []))
        total = playlists_response.get('total')

    # Remove any playlists that we don't own
    playlists = [playlist for playlist in playlists if playlist.get('owner', {}).get('id') == username]

    # List out all of the playlists
    print_header('Your Playlists', 30)
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
        tracks_response = sp.user_playlist_tracks(playlist_owner, playlist.get('id'), offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

    # Print out our tracks along with the list of artists for each
    print_header('Tracks in "{}"'.format(playlist.get('name'), 30))
    for i, track in enumerate(tracks):
        track_info = track.get('track')
        artist_names = ', '.join([artist.get('name') for artist in track_info.get('artists', [])])
        print('  {}) {} - {}'.format(i + 1, track_info.get('name'), artist_names))

    # Choose some tracks
    track_choices = input('\nChoose some tracks (e.g 1,4,5,6,10): ')

    # Turn the input into a list of integers
    track_choice_indexes = [int(choice.strip()) for choice in track_choices.split(',')]

    # Grab the tracks from our track list and build a map of id->track
    selected_tracks = [tracks[index - 1].get('track') for index in track_choice_indexes]
    track_map = {track.get('id'): track for track in selected_tracks}

    # Request the audio features for the chosen tracks (limited to 50)
    tracks_features = sp.audio_features(tracks=track_map.keys())

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

    # Iterate through the features and print the track and info
    print_header('Audio Features', 30)
    for track_features in tracks_features:
        track_id = track_features.get('id')
        track = track_map.get(track_id)
        artist_names = ', '.join([artist.get('name') for artist in track.get('artists', [])])
        print('\n  {} - {}'.format(track.get('name'), artist_names))
        for feature in desired_features:
            # Pull out the value of the feature from the features
            feature_value = track_features.get(feature)

            # If this feature is the key, convert it to a readable pitch
            if feature == 'key':
                feature_value = translate_key_to_pitch(feature_value)

            # Print the feature value
            print('    {}: {}'.format(feature, feature_value))


def get_token(username):
    """
    Given username, authenticate the client and return a token
    (NOTE: You will have to paste the URL from your browser back into the terminal)
    :param username:
    :return:
    """
    try:
        with open('credentials.json') as f:
            credentials = json.load(f)

            # Get an auth token for this user
            token = sp_util.prompt_for_user_token(username,
                                                  client_id=credentials.get('client_id'),
                                                  client_secret=credentials.get('client_secret'),
                                                  redirect_uri=credentials.get('redirect_uri',
                                                                               'http://localhost/callback'),
                                                  scope=scope)

            return token
    except IOError as e:
        print('Unable to find/read credentials.json file.  Please see README for instructions on creating this file.')
        sys.exit(1)


if __name__ == '__main__':
    main()
