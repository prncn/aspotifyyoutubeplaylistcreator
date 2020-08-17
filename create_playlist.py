from __future__ import print_function
import json
import requests
import youtube_dl
import youtube_dl.utils
youtube_dl.utils.std_headers['User-Agent'] = 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
TRACKS = []
IMAGES = []


# Add all liked YouTube (songs) into TRACKS
def list_likes(youtube, spotify):
    TRACKS.clear()
    IMAGES.clear()
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like",
        maxResults=5
    )
    response = request.execute()

    for item in response["items"]:
        youtube_url = "https://www.youtube.com/watch?v={}".format(item['id'])
        video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
        song_name = video["track"]
        artist = video["artist"]
        print("new", item['snippet']['title'], song_name, artist)

        if song_name is not None:
            TRACKS.append(
                search_track(song_name, artist, spotify)
            )


# Create empty Spotify playlist
# Return playlist ID
def post_empty_playlist(user_id, spotify):
    query = "https://api.spotify.com/v1/users/{}/playlists".format(user_id)
    response = requests.post(
        query,
        data=json.dumps({
            "name": "TUBIFY_",
            "description": "auto generated through youtube api",
            "public": True
        }),
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()

    return response_json["id"]


# Search spotify with the YouTube track as query and add album cover to IMAGES.
# Return Spotify URI
def search_track(song_name, artist, spotify):
    query = "https://api.spotify.com/v1/search?q=track:{}%20artist:{}&type=track".format(
        song_name,
        artist
    )
    response = requests.get(
        query,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()
    songs = response_json['tracks']['items']

    if len(songs) == 0:
        uri = 'HKMfOA7SBN7XqV4fiTnvK'
    else:
        uri = songs[0]['uri']
        img_resp = requests.get(
            "https://api.spotify.com/v1/tracks/{}".format(songs[0]['id']),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify)
            }
        )
        img_json = img_resp.json()
        IMAGES.append(img_json['album']['images'][0]['url'])

    return uri


# Return playlist cover
def get_playlist_cover(spotify, playlist_id):
    query = "https://api.spotify.com/v1/playlists/{}/images".format(playlist_id)
    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()
    if len(response_json) == 0:
        cover_img = "https://i.scdn.co/image/ab67616d0000b273c4d71ef52f65999138c6bb10"
    else:
        # cover_img = response_json[0]['url']
        cover_img = IMAGES[0]

    return cover_img


# Utility. Return this user's Spotify ID
def get_user_id(spotify):
    query = "https://api.spotify.com/v1/me"
    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()
    current_user_id = response_json['id']

    return current_user_id


# Return Spotify profile image
def get_profile_img(spotify):
    query = "https://api.spotify.com/v1/me"
    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()
    profile_img = response_json['images'][0]['url']

    return profile_img


# Wrapper function to add all tracks to the empty playlist
def finalise_playlist(user_id, youtube, spotify):
    list_likes(youtube, spotify)
    uris = TRACKS
    playlist_id = post_empty_playlist(user_id, spotify)
    request_data = json.dumps(uris)

    query = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id)
    requests.post(
        query,
        data=request_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer {}".format(spotify)
        }
    )

    return playlist_id


# Test function to clear dictionary data during server run (fixed)
def clean_song_cache():
    global TRACKS
    TRACKS = {}
