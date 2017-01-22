import json
import sys
import spotipy
import spotipy.util as sp_util

# Define the scopes that we need access to
# https://developer.spotify.com/web-api/using-scopes/
scope = 'user-library-read playlist-read-private'


def print_header(message, length=50):
    # Print a little message
    print('\n' + ('*' * length))
    print(message)
    print('*' * length)


def main():
    """
    Our main function that will get run when the program executes
    """
    print_header('Spotify Web API Demo App')

    # Run our demo function
    retry = True
    while retry:
        # Run our demo script
        demo()

        # Prompt the user to run again
        retry_input = input('\nRun the program again? (Y/N): ')
        retry = retry_input.lower() == 'y'


def demo():
    # Prompt the user for their username
    # username = input('\nWhat is your spotify username: ')
    username = 'markster3910'

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
    # The API paginates the results, so we need to iterate
    while len(tracks) < total:
        tracks_response = sp.user_playlist_tracks(playlist_owner, playlist.get('id'), offset=len(tracks))
        tracks.extend(tracks_response.get('items', []))
        total = tracks_response.get('total')

    for i, track in enumerate(tracks):
        track_info = track.get('track')
        artist_names = ', '.join([artist.get('name') for artist in track_info.get('artists', [])])
        print('  {}) {} - {}'.format(i, track_info.get('name'), artist_names))


def get_token(username):
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
