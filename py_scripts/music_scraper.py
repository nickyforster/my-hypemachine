import feedparser
import requests
import json
from bs4 import BeautifulSoup
import re

feed_to_feed_search = {
    'largeheartedboy': re.compile('^shorties.*$'),
    'killing-moon': re.compile('^totd.*$')
}

feed_to_page_search = {
    'largeheartedboy': re.compile('^stream'),
}

song_url_targets = re.compile(r'(apple.com)|(bandcamp.com)|(spotify.com)|(soundcloud.com)')
def check_iframe_url(url):
    return song_url_targets.search(url)

def scrape_soundcloud(url):
    pass
def scrape_bandcamp(url):
    pass
def scrape_spotify(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    song_json = json.loads(soup.find('script', {'id': 'resource'}).text)
    track_items = song_json['tracks']['items']
    tracks_to_return = []
    for item in track_items:
        track_to_add = {}
        #artist will be the first artist in this list
        item_keys = item.keys()
        if 'artists' in item_keys:
            track_to_add['artist'] = item['artists'][0]['name']
            track_to_add['song'] = item['name']
            tracks_to_return.append(track_to_add)
        elif 'track' in item_keys: ## This is probably a playlist
            track_to_add['artist'] = item['track']['artists'][0]['name']
            track_to_add['song'] = item['track']['name']
            tracks_to_return.append(track_to_add)

    return tracks_to_return
def scrape_apple(url):
    pass

domain_to_scraper = {
    'soundcloud.com': scrape_soundcloud,
    'bandcamp.com': scrape_bandcamp,
    'spotify.com': scrape_spotify,
    'apple.com': scrape_apple
}

class ScrapeSession:
    def __init__(self):
        self.blog_list = [
            ('largeheartedboy','http://feeds.feedburner.com/largeheartedboy'),
            ('killing-moon','http://www.killing-moon.com/feed')
        ]
    
    
    def get_song_links(self):
        song_endpoints = []
        for blog in self.blog_list[:1]:
            page_links = []
            feed = feedparser.parse(blog[1])
            for entry in feed['entries']:
                if feed_to_feed_search[blog[0]].search(entry['title'].lower()):
                    page_links.append(entry['links'][0]['href'])

            for link in page_links:
                soup = BeautifulSoup(requests.get(link).text, 'html.parser')
                content_links = soup.find_all('a')
                if blog[0] in feed_to_page_search.keys():
                    for content_link in content_links:
                        test_text = content_link.find_parent('p')
                        if test_text:
                            if feed_to_page_search[blog[0]].search(test_text.text.lower()):
                                song_endpoints.append(content_link['href'])
                else:
                    song_endpoints.append(link)
        return song_endpoints
    
    def get_song_data(self, song_list):
        song_data = []
        for endpoint in song_list:
            soup = BeautifulSoup(requests.get(endpoint).text, 'html.parser')
            iframes = soup.find_all('iframe')
            endpoints_with_domain = []
            for iframe in iframes:
                if 'src' in iframe.attrs:
                    url_match = check_iframe_url(iframe['src'])
                    if url_match:
                        endpoints_with_domain.append((url_match.group(), iframe['src']))
            for endpoint in endpoints_with_domain[:1]:
                # print(endpoint[1])
                scrape_result = domain_to_scraper[endpoint[0]](endpoint[1])
                if scrape_result:
                    song_data += scrape_result
        return song_data
