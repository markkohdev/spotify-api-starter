import json
import sys
import spotipy
import spotipy.util as sp_util

scope = 'user-library-read'


def main():
    """
    Our main function that will get run when the program executes
    """
    # Run our demo function
    retry = True
    while retry:
        # Run our demo script
        demo()

        # Prompt the user to run again
        retry_input = input('Run the program again? (Y/N): ')
        retry = retry_input.lower() == 'y'


def demo():
    # Prompt the user for their username
    username = input('What is your spotify username: ')

    # Initialize Spotipy
    token = get_token(username)
    sp = spotipy.Spotify(auth=token)

    # Get all the playlists for this user
    playlists_response = sp.user_playlists(username)
    playlists = playlists_response.get('items', [])

    # List out all of the playlists
    for i, playlist in enumerate(playlists):
        print('  {}.) {} - {}'.format(i + 1, playlist.get('name'), playlist.get('uri')))

    # Choose a playlist
    playlist_choice = int(input('Choose a playlist: '))
    playlist = playlists[playlist_choice - 1]
    playlist_owner = playlist.get('owner', {}).get('id')


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
