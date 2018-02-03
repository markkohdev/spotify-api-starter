# display_utils.py
#
# This file contains convenience functions for displaying data from the Spotify
# API and for propmpting users for input
#
# Written by Mark Koh
# 2/3/2018
import json

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


def translate_key_to_pitch(key):
    """
    Given a Key value in Pitch Class Notation, map the key to its actual pitch string
    https://en.wikipedia.org/wiki/Pitch_class
    :param key: The integer key
    :return: The translated Pitch Class string
    """
    pitches = ['C', 'C♯/D♭', 'D', 'D♯/E♭', 'E', 'F', 'F♯/G♭', 'G', 'G♯/A♭', 'A', 'A♯/B♭', 'B']
    return pitches[key]


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
        'mode',
        'loudness',
        'energy',
        'danceability',
        'acousticness',
        'instrumentalness',
        'liveness',
        'speechiness',
        'valence'
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


def print_audio_analysis_for_track(track, track_analysis):
    """
    Given a track and a analysis response, print out the analysis JSON
    :param track:
    :param track_analysis:
    :return:
    """
    print('\n  {}'.format(track_string(track)))
    print(json.dumps(track_analysis, indent=2))


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