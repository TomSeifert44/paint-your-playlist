import base64
import requests
import matplotlib.image as mpimg
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)  # or DEBUG, WARNING, ERROR

def retrieve_playlists(client_id, client_secret, redirect_uri, code):
    """
    Retrieves information from Spotify API about a given user's playlists, the user's ID, and a token to access further Spotify API resources

    Args:
        client_id (string): The application's client key
        client_secret (string): The application's client secret key
        redirect_uri (string): The url that Spotify routes to after a user logs in successfully

    Returns:
        string: access token for further Spotify API access
        dict: dictionary of a user's playlist info
        string: user id
    """
    # need to encode credentials in base64 for headers - used AI to find out what packages to use to do so (Chat-GPT 15 May 2025)
    # redirected to base64 docs (base64 docs 15 May 2025)

    # use encode() to turn string into bytes (base64 docs 15 May 2025)
    credential_bytes = f"{client_id}:{client_secret}".encode()

    # use base64.b64encode() to encode bytes in base64 (base64 docs 15 May 2025)
    creds_base64 = base64.b64encode(credential_bytes)

    # convert bytes back to string to create authentication header (base64 docs 15 May 2025)
    auth_header = creds_base64.decode()

    # define headers for requesting an access code from Spotify API (Spotify API 15 May 2025) 
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # define data for requesting an access code from Spotify API using authorization code `code` (Spotify API 15 May 2025)
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }

    # define url for requesting an access code from Spotify API (Spotify API 15 May 2025)
    token_url = "https://accounts.spotify.com/api/token"

    # use POST method from python requests package to get user-specific access token (requests docs 15 May 2025)
    response = requests.post(token_url, data=data, headers=headers)

    # create dictionary from JSON object (requests docs 15 May 2025)
    response_dict = response.json()

    # get access token value from response dictionary
    access_token = response_dict.get("access_token")

    # redefine headers for use in retrieving user data from Spotify API (Spotify API 15 May 2025)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # use get request to retrieve user's data from Spotify API (Spotify API 15 May 2025)
    user_res = requests.get("https://api.spotify.com/v1/me", headers=headers)

    # create dictionary of user info from JSON object (requests docs 15 May 2025)
    user_info = user_res.json()

    # get user id from user info
    user_id = user_info["id"]

    # use get request to retrieve user's playlists from Spotify API (Spotify API 15 May 2025)
    playlists_res = requests.get("https://api.spotify.com/v1/me/playlists", headers=headers)

    # create dictionary of playlist info from JSON object (requests docs 15 May 2025)
    playlists_info = playlists_res.json()

    # return access token, playlist info dict, and user id from Spotify
    return access_token, playlists_info, user_id

def retrieve_playlist_info(access_token, playlist_id):
    """
    Retrieves song-level data from Spotify API for a specified playlist in the user's library

    Args:
        access_token (string): The access token for the request
        playlist_id (string): The playlist's id

    Returns:
        dict: dictionary of song info for playlist given

    """

    # define headers for the request (Spotify API 15 May 2025)
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # use get request to retrieve playlist's song data from Spotify API (Spotify API 15 May 2025)
    selected_playlist_res = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}', headers=headers)
    # create dictionary of playlist's song data from JSON object (requests docs 15 May 2025)
    selected_playlist_info = selected_playlist_res.json()

    # initialize dictionary to store cleaned song info
    song_info = {}

    # clean song info
    for item in selected_playlist_info["tracks"]["items"]:
        track = item["track"]
        if track:
            song_name = track["name"]
            if track["id"]:

                song_info[song_name] = {
                    "album": track["album"]["name"],
                    "id": track["id"],
                    "artists": [artist["name"] for artist in track["artists"]],
                    "popularity": track["popularity"],
                    "image_url" : track["album"]["images"][0]["url"]
                }
        else:
            continue

    # return dictionary of song info
    return song_info


def retrieve_image_urls(song_info):
    """
    Retrieves cover images for songs in custdom dictionary 

    Args:
        song_info (dict): dictionary containing song information

    Returns:
        list: list of urls for song cover images 

    """

    # get song ids
    song_ids = [song_info[song]["id"] for song in song_info]

    # get urls
    image_urls = [song_info[song]["image_url"] for song in song_info]

    # return urls
    return image_urls

def upload_to_spotify(access_token, playlist_id):
    """
    Upload's image to Spotify and sets it as specified playlist's cover image

    Args:
        access_token (string): The access token for the request
        playlist_id (string): The playlist's id

    Returns:
        empty: request response

    """

    # define image path (tempfile/Flask_Session docs 3 Jun 2025)
    image_path = "/tmp/output.png"

    img_png = mpimg.imread(image_path)

    # save as jpg
    mpimg.imsave('/tmp/output.jpg', img_png)

    # read jpg as binary to get bytes (open docs 3 Jun 2025)
    with open('/tmp/output.jpg', 'rb') as image_file:
        jpeg_bytes = image_file.read()

    # encode image in base64 (base64 docs 3 Jun 2025)
    encoded_image = base64.b64encode(jpeg_bytes).decode("utf-8")

    # define headers for the request (Spotify API 3 Jun 2025)
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "image/jpeg"
    }

    # make PUT request (Spotify API 3 Jun 2025)
    response = requests.put(
        f"https://api.spotify.com/v1/playlists/{playlist_id}/images",
        headers=headers,
        data=encoded_image
    )

    # return response of request
    return response