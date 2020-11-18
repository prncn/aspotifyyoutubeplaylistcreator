from __future__ import print_function
import json
import requests
IMG_URLS = []
NAMES = []
LINKS = []
URIS = []


def get_playlists(spotify):
    IMG_URLS.clear()
    NAMES.clear()
    LINKS.clear()
    URIS.clear()
    query = "https://api.spotify.com/v1/me/playlists?limit=40"
    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    pl_info = response.json()
    # print(pl_info['items'])
    # print(response)
    # print(pl_info['items'][0]['name'])
    # names = [item['name'] for item in pl_info['items']]
    # img_urls = [item['images'][0]['url'] for item in pl_info['items']]
    # print(pl_info['items'][0]['images'])

    for item in pl_info['items']:
        if len(item['images']) != 0:
            IMG_URLS.append(item['images'][0]['url'])
        NAMES.append(item['name'].lower())
        LINKS.append(item['external_urls']['spotify'])
        URIS.append(item['uri'])


def start_playback(spotify, uri):
    query = "https://api.spotify.com/v1/me/player/play"

    response = requests.put(
        query,
        data=json.dumps({
            "context_uri": uri,
            "position_ms": 25000
        }),
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    # print(response)
    # print(response.json())


def stop_playback(spotify):
    query = "https://api.spotify.com/v1/me/player/pause"
    response = requests.put(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    # print(response.json())


def get_device_id(spotify):
    query = "https://api.spotify.com/v1/me/player/devices"

    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    devices = response.json()
    # print(devices)
    for device in devices['devices']:
        if device['name'] == 'Tubify Playback':
            print(device['id'])
            return device['id']


if __name__ == '__main__':
    # start_playback()
    stop_playback('BQDsVUbpfbYHRkAppGm7cRyCEPGDvfJyne2JtvbjLNy0SQewQseFz-dsaDRWJr7jtAHNT-0ggwc09xWBlznUJ7VIKOAxsCEgUiyzsfCLDnZyopUlo5VQBXKSOzysX5Lwn89PJegccB1N5vOb3WcN9S_FuOfo7Aq0eHNTb7JVppBwywK5ulTJrM-AMzOEMTkzKHGJxuulJJLcx0slwjoakC4qK0Gz4HSYtsz1EisKiw0prd3pbneJ1HrylbXIz8ufscFcLUZFrY0w')
    # print(PLAYLISTS)
