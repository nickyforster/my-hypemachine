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
    pass
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
        print(song_list)
        for endpoint in song_list:
            soup = BeautifulSoup(requests.get(endpoint).text, 'html.parser')
            iframes = soup.find_all('iframe')
            endpoints_with_domain = []
            for iframe in iframes:
                if 'src' in iframe.attrs:
                    url_match = check_iframe_url(iframe['src'])
                    if url_match:
                        endpoints_with_domain.append((url_match, iframe['src']))
            
                # iframe_soup = BeautifulSoup(requests.get(iframe['src']).content, 'html.parser')
                # print(iframe_soup.prettify())
        

# largeheart = 'http://feeds.feedburner.com/largeheartedboy'
# killing_moon = "http://www.killing-moon.com/feed"
# songs = []

# km_parse = feedparser.parse(killing_moon)
# link = km_parse['entries'][1]['link']
# print(link)

# km_page = requests.get(link)
# km_soup = BeautifulSoup(km_page.content, 'html.parser')
# iframe = km_soup.find('iframe')
# iframe_soup = BeautifulSoup(requests.get(iframe['src']).content, 'html.parser')
# song_json = json.loads(iframe_soup.find('script', {'id': 'resource'}).text)
# if song_json['album']['album_type'] == 'single':
#     song = song_json['album']['name']
#     artist = song_json['album']['artists'][0]['name']
#     songs.append({'song': song, 'artist': artist})
# else: 
#     print(f'Not a single')

# print(songs)