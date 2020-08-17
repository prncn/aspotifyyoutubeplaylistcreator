import create_playlist
import artist_analysis
import display_collection
from flask import Flask, request, redirect, render_template, session, url_for
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json
from urllib.parse import quote
import random
import string

app = Flask(__name__)
app.secret_key = 'yvibahfm'
executed = False

# Google API Authentication
YT_SCOPES = ["https://www.googleapis.com/auth/youtube", "https://www.googleapis.com/auth/youtube.readonly"]
YT_API_SERVICE_NAME = 'youtube'
YT_API_VERSION = 'v3'
client_secret = {"web": {
    "client_id": "537402813839-p931d64jegt8tvvrnp4tu02irltht58l.apps.googleusercontent.com",
    "client_secret": "dNuMTyXZaiA4YINeQYXHaphq",
    "redirect_uris": ["https://localhost:8080/oauth2callback"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://accounts.google.com/o/oauth2/token",
    "YOUR_API_KEY": "AIzaSyCtjvnhzsdOqwJ6cj-OklVXsBFBqxlfMg8"
    }
}

#  Spotify API Authentication
SP_CLIENT_ID = "b3476355e8434cdea6c69faf524c8db3"
SP_CLIENT_SECRET = "e349effa6ee3489ba63c56ab59cae285"
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_URL = "https://api.spotify.com/v1"
REDIRECT_URI = "https://localhost:8080/callback/"
SCOPE = "playlist-modify-public user-top-read user-modify-playback-state streaming user-read-email user-read-playback-state"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": SP_CLIENT_ID
}

app.config["SESSION_PERMANENT"] = False
NO_PROFILE_IMG = 'https://cdn3.iconfinder.com/data/icons/mixed-communication-and-ui-pack-1/48/general_pack_NEW_glyph_profile-512.png'


@app.route('/')
def index():
    profile_img = get_profile_img()
    if 'token' in session:
        spotify = session.get('token')
        display_collection.stop_playback(spotify)

    return render_template('index.html', profile_img=profile_img)


@app.route('/created')
def created():
    profile_img = get_profile_img()
    image_url = create_playlist.IMAGES
    return render_template('success-playlist.html', profile_img=profile_img, image_url=image_url)


@app.route('/nonefound')
def nonefound():
    profile_img = get_profile_img()
    return render_template('fail.html', profile_img=profile_img)


@app.errorhandler(404)
def page_not_found(error):
    profile_img = get_profile_img()
    return render_template('fail.html', profile_img=profile_img, msg="404 page doesn't exist :("), 404


@app.errorhandler(500)
def internal_failure(error):
    profile_img = get_profile_img()
    return render_template('fail.html', profile_img=profile_img, msg="500 bad coding."), 500


@app.route('/fetchlikes')
def external_one():
    if 'token' not in session:
        session['caller'] = '/fetchlikes'
        return redirect('spotyauth')

    if 'credentials' not in session:
        session['caller'] = '/fetchlikes'
        return redirect('oauth2auth')

    spotify = session.get('token')
    credentials = google.oauth2.credentials.Credentials(
        **session['credentials'])
    youtube = googleapiclient.discovery.build(
        YT_API_SERVICE_NAME, YT_API_VERSION, credentials=credentials, cache_discovery=False)
    user_id = create_playlist.get_user_id(spotify=spotify)

    playlist_id = create_playlist.finalise_playlist(user_id=user_id, youtube=youtube, spotify=spotify)
    session['credentials'] = credentials_to_dict(credentials)

    if not create_playlist.TRACKS:
        return redirect('/nonefound')

    return redirect('/created')


@app.route('/listenhabits')
def external_two():
    if 'token' not in session:
        session['caller'] = '/listenhabits'
        return redirect('spotyauth')

    profile_img = get_profile_img()
    spotify = session.get('token')
    artist_analysis.get_top_artists(spotify)

    if 'genderstat' not in session:
        gender = artist_analysis.get_gender()
        session['genderstat'] = gender
    else:
        gender = session.get('genderstat')

    popular = artist_analysis.get_popular()
    topvalues = artist_analysis.get_topgenre()
    topnames = list(artist_analysis.GENRES)
    # print(artist_analysis.IMAGES)
    # l_names = [name.lower() for name in artist_analysis.NAMES]

    return render_template('success-artists.html', profile_img=profile_img, mgen=gender['male'],
                           fgen=gender['female'], npop=popular['niches'], ppop=popular['pops'],
                           topv=topvalues, topn=topnames, toplen=len(topnames),
                           a_names=artist_analysis.URIS, images=artist_analysis.IMAGES, artlen=len(artist_analysis.IMAGES))


def str_(prc):
    return "{:.1f}".format(prc)


@app.route('/collection')
def external_three():
    if 'token' not in session:
        session['caller'] = '/collection'
        return redirect('spotyauth')

    profile_img = get_profile_img()
    spotify = session.get('token')
    display_collection.get_playlists(spotify)
    # display_collection.start_playback(spotify, 'spotify:playlist:4jJzFoC5QiXiCiN8mcHLWt')
    # (display_collection.PLAYLISTS[0])
    return render_template('success-display.html', profile_img=profile_img,
                           pl_images=display_collection.IMG_URLS, pl_names=display_collection.NAMES,
                           pl_links=display_collection.LINKS, pl_count=len(display_collection.IMG_URLS),
                           pl_uris=display_collection.URIS, sp_token=spotify)


@app.route('/collection/playback?<playlist_id>')
def playback_playlist(playlist_id):
    spotify = session.get('token')
    display_collection.start_playback(spotify, playlist_id)
    return "", 204


@app.route('/oauth2auth')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_secret, scopes=YT_SCOPES)
    flow.redirect_uri = client_secret['web']['redirect_uris'][0]
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state

    return redirect(authorization_url)


@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')

    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_config=client_secret, scopes=YT_SCOPES, state=state)
    flow.redirect_uri = client_secret['web']['redirect_uris'][0]
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(session.get('caller'))


@app.route('/spotyauth')
def spotyauth():
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route('/callback/')
def callback():
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        'client_id': SP_CLIENT_ID,
        'client_secret': SP_CLIENT_SECRET,
    }
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    session['token'] = access_token

    profile_img = create_playlist.get_profile_img(access_token)
    session['profile_img'] = profile_img

    return redirect(session.get('caller'))


@app.route('/logout')
def clear_credentials():
    if 'credentials' in session:
        del session['credentials']
    if 'token' in session:
        del session['token']
    session.clear()
    # app.secret_key = randomString()
    return redirect('/')


@app.route('/login')
def load_credentials():
    if 'token' not in session:
        session['caller'] = url_for('index')
        return redirect('spotyauth')

    if 'credentials' not in session:
        session['caller'] = url_for('index')
        return redirect('oauth2auth')
    return redirect('/')


def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}


def get_profile_img():
    if 'profile_img' not in session:
        profile_img = NO_PROFILE_IMG
    else:
        profile_img = session.get('profile_img')

    return profile_img


def random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(8))


if __name__ == '__main__':
    app.run('localhost', debug=True, port=8080, ssl_context=('server.crt', 'server.key'), threaded=True)
