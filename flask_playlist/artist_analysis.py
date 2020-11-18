from __future__ import print_function
import json
import requests

NAMES = []
URIS = []
POPS = []
IMAGES = []
GENRES = {}
RATIO = {'male': 0,
         'female': 0,
         'group': 0,
         'pops': 0,
         'niches': 0,
         'n/a': 0}
last_fm = '74276898ee7faad0825b302a0abe5f07'
method = 'http://ws.audioscrobbler.com/2.0/?'


def get_top_artists(spotify):
    global GENRES
    NAMES.clear()
    POPS.clear()
    IMAGES.clear()
    GENRES.clear()
    query = "https://api.spotify.com/v1/me/top/artists?limit=45"
    response = requests.get(
        query,
        headers={
            "Authorization": "Bearer {}".format(spotify)
        }
    )
    response_json = response.json()
    for item in response_json['items']:
        NAMES.append(item['name'])
        URIS.append(item['external_urls']['spotify'])
        POPS.append(item['popularity'])
        IMAGES.append(item['images'][1]['url'])
        for genre in item['genres']:
            if genre not in GENRES:
                GENRES[genre] = 0
            GENRES[genre] += 1

    GENRES = {k: v for k, v in sorted(GENRES.items(), key=lambda key: key[1], reverse=True)}


def contains_word(s, w1, w2):
    return (' ' + w1 + ' ') in (' ' + s + ' ') or (' ' + w2 + ' ') in (' ' + s + ' ')


def fetch_bio(musician):
    query = "{}method=artist.getinfo&artist={}&api_key={}&format=json".format(method, musician,
                                                                              last_fm)
    response = requests.get(query)
    if not response.ok:
        return None
    bio = response.json()
    bio_content = bio['artist']['bio']['summary']

    if contains_word(bio_content, 'he', 'his'):
        # print('MALE:', musician)
        RATIO['male'] += 1
    if contains_word(bio_content, 'she', 'her'):
        # print('FEMALE:', musician)
        RATIO['female'] += 1
    # if re.search(r'\b(?:they|their)\b', bio_content, re.IGNORECASE):
        # print('GROUP:', musician)
        # RATIO['group'] += 1


def fetch_similars(musician):
    query = "{}method=artist.getsimilar&artist={}&api_key={}&format=json".format(method, musician, last_fm)
    response = requests.get(query)
    if not response.ok:
        return None
    info = response.json()
    similars = [artist['name'] for artist in info['similarartists']['artist'] if '&' not in artist['name']]
    # print(similars)
    # print(info['similarartists']['artist'])
    return similars


def get_topgenre():
    data = []
    all_count = sum(GENRES.values())
    as_list = list(GENRES.values())
    for i in range(len(as_list)):
        data.append(round(as_list[i] / all_count * 100, 2))

    return data


def get_gender():
    data = {
        'male': 0,
        'female': 0,
    }
    for name in NAMES:
        fetch_bio(name)

    male_rate = RATIO['male'] / (RATIO['male'] + RATIO['female'])
    female_rate = RATIO['female'] / (RATIO['male'] + RATIO['female'])
    # print("MEN: ", "{:.1%}".format(male_rate), " WOMEN: ", "{:.1%}".format(female_rate))

    RATIO['male'] = 0
    RATIO['female'] = 0
    RATIO['group'] = 0

    data['male'] = round(male_rate * 100, 2)
    data['female'] = round(female_rate * 100, 2)

    return data


def get_popular():
    data = {
        'niches': 0,
        'pops': 0
    }
    for pop in POPS:
        if pop < 50:
            RATIO['niches'] += 1
        if pop > 70:
            RATIO['pops'] += 1

    niches_rate = RATIO['niches'] / (len(POPS))
    pop_rate = RATIO['pops'] / (len(POPS))

    RATIO['niches'] = 0
    RATIO['pops'] = 0

    data['niches'] = round(niches_rate * 100, 2)
    data['pops'] = round(pop_rate * 100, 2)

    return data


def degrees_network(start, end, seen, iterator):
    for artist in fetch_similars(start):
        # print(artist)
        if artist == end:
            return True
    else:
        for current in fetch_similars(start):
            # print(current)
            if current in seen:
                continue
            if end in fetch_similars(current):
                print('here')
                return True

        for newstart in fetch_similars(start):
            if iterator > 5:
                return False

            if newstart in seen:
                continue
            print(newstart)
            seen.add(newstart)
            if degrees_network(newstart, end, set, iterator+1):
                return True

    return False


def degrees_wrapper(start, end):
    seen = set()
    found = degrees_network(start, end, seen, 0)
    seen.clear()
    return found


# if __name__ == '__main__':
