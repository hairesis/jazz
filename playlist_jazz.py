from __future__ import unicode_literals, print_function
import csv
import youtube_dl
import requests
import json


def artists(track):
    return [artist['name'] for artist in track['artists']]


def song_title(track):
    return track['name']


def album_title(track):
    return track['album']['name']

def popularity(track):
    return track['popularity']

def download_playlist(url, session):
    
    while url is not None:
        playlist = session.get(url)
        playlist = playlist.json()
        url = playlist['next']

        for track in [item['track'] for item in playlist['items']]:
            yield (album_title(track), song_title(track), artists(track), popularity(track))
            

def connection():
    session = requests.Session()
    session.headers.update(
        {'Authorization': 'Bearer ...',
         'Accept': 'application/json'}
    )
    return session


def download_tracks(tracks):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }]
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download(tracks)

        
def load_playlist():
    result = []
    try:
        with open('playlist.csv', 'r') as playlist:
            reader = csv.DictReader(playlist)
            for row in reader:
                result.append(row)
            return result
    except FileNotFoundError:
        print('Playlist not found, download ...')
        with open('playlist.csv', 'w') as f_playlist:
            playlist = download_playlist(url, connection())
            fieldnames = ['Album', 'Track', 'Artist(s)', 'Popularity', 'Youtube URL']
            writer = csv.DictWriter(f_playlist, fieldnames=fieldnames)
            writer.writeheader()
            for album, track, artists, pop in sorted(playlist, key=lambda x: x[3], reverse=True):
                artists = ' '.join([a.replace(',', ' ') for a in artists])
                row = {'Album': album,
                       'Track': track.replace(',', ' '),
                       'Artist(s)': artists,
                       'Popularity': pop,
                       'Youtube URL': ''}
                result.append(row)
                writer.writerow(row)
    return result


def youtube_URL_filter(playlist):
    return [item['Youtube URL'] for item in playlist if item['Youtube URL']]

    
if __name__ == '__main__':

    download_tracks(youtube_URL_filter(load_playlist()))
