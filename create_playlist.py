from __future__ import print_function
import json
import requests
import youtube_dl
import youtube_dl.utils
youtube_dl.utils.std_headers['User-Agent'] = 'facebookexternalhit/1.1 (+http://www.facebook.com/externalhit_uatext.php)'
ALL_SONG_INFO = {}
IMAGES = []


def get_liked_videos(youtube, spotify):
    ALL_SONG_INFO.clear()
    IMAGES.clear()
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        myRating="like",
        maxResults=20
    )
    response = request.execute()

    for item in response["items"]:
        video_title = item["snippet"]["title"]
        youtube_url = "https://www.youtube.com/watch?v={}".format(item['id'])

        video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)
        song_name = video["track"]
        artist = video["artist"]

        if song_name is not None:
            print(song_name, " - ", artist)
            ALL_SONG_INFO[video_title] = {
                "youtube_url": youtube_url,
                "song_name": song_name,
                "artist": artist,
                "spotify_uri": get_spotify_uri(song_name, artist, spotify)
            }


def _get_liked_videos(youtube, spotify):
    song_name = 'All Mine'
    artist = 'Kanye West'
    ALL_SONG_INFO['default'] = {
        "spotify_uri": get_spotify_uri(song_name, artist, spotify)
    }


def check_no_likes(youtube):
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

        if song_name is not None:
            return True

    if not ALL_SONG_INFO:
        return False


def create_playlist(user_id, spotify):
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


def get_spotify_uri(song_name, artist, spotify):
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
        # print(img_json['album']['images'])
        IMAGES.append(img_json['album']['images'][0]['url'])

    return uri


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


def add_song_to_playlist(user_id, youtube, spotify):
    get_liked_videos(youtube, spotify)
    uris = [info["spotify_uri"] for song, info in ALL_SONG_INFO.items()]

    print(IMAGES)

    playlist_id = create_playlist(user_id, spotify)
    request_data = json.dumps(uris)
    print(request_data)
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


def clean_song_cache():
    global ALL_SONG_INFO
    ALL_SONG_INFO = {}
