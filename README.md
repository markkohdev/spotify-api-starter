# Getting Started with the Spotify Web API
## For Python
Get up and running with the Spotify Web API using Python

**Some handy documentation:**
 - Web API Documentation - https://developer.spotify.com/web-api/
 - Spotipy Documentation - http://spotipy.readthedocs.io/en/latest/

   
 
## Setup
First, we need to make sure python3, pip, and virtualenv are installed on your system.
To install this stuff, run
```
./setup.sh
source ~/.bashrc
```

Go to https://developer.spotify.com/my-applications and create a new Application.  Add your credentials to a file called
`credentials.json` in the root of this repo that looks like this:
```
{
  "client_id": "your-spotify-client-id",
  "client_secret": "your-spotify-client-secret",
  "redirect_uri": "your-app-redirect-url"
}
```
If you're not sure what to put for your redirect URI, just add `http://localhost/callback` to your "Redirect URIs" in your 
Application page.


## Running
To run the out of the box demo, simply run
```
make run
```
