import feedparser
import requests
import json
from bs4 import BeautifulSoup

largeheart = 'http://feeds.feedburner.com/largeheartedboy'
killing_moon = "http://www.killing-moon.com/feed"
songs = []

km_parse = feedparser.parse(killing_moon)
link = km_parse['entries'][1]['link']
print(link)

km_page = requests.get(link)
km_soup = BeautifulSoup(km_page.content, 'html.parser')
iframe = km_soup.find('iframe')
iframe_soup = BeautifulSoup(requests.get(iframe['src']).content, 'html.parser')
song_json = json.loads(iframe_soup.find('script', {'id': 'resource'}).text)
if song_json['album']['album_type'] == 'single':
    song = song_json['album']['name']
    artist = song_json['album']['artists'][0]['name']
    songs.append({'song': song, 'artist': artist})
else: 
    print(f'Not a single')

print(songs)