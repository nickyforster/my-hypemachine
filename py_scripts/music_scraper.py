import feedparser
import requests
import json
from bs4 import BeautifulSoup
import re
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

chrome_options = Options()
chrome_options.set_headless()
assert chrome_options.headless
chrome_browser = Chrome(options=chrome_options)

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
    tracks_to_return = []
    chrome_browser.get(url)
    try:
        element = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "title__h2Text"))
        )
    except TimeoutException:
        print("Loading took too much time!")

    ## text method returns a tuple...?
    soundcloud_title = chrome_browser.find_element_by_class_name('title__h2Text'),
    soundcloud_title = soundcloud_title[0].text
    track = soundcloud_title.split('by')[0].strip()
    artist = soundcloud_title.split('by')[1].strip()
    track_to_add = {
        'artist': artist,
        'song': track
    }

    tracks_to_return.append(track_to_add)
    return tracks_to_return

def scrape_bandcamp(url):
    tracks_to_return = []
    chrome_browser.get(url)
    try:
        element = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.ID, "albumtrackartistrow"))
        )
        element_two = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.ID, "currenttitle_title"))
        )
        element_three = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.ID, "maintextlink"))
        )
    except TimeoutException:
        print("Loading took too much time!")
    track_to_add = {
        'artist': chrome_browser.find_element_by_id('albumtrackartistrow').text,
        'song': chrome_browser.find_element_by_id('currenttitle_title').text
    }
    if not track_to_add['song']:
        track_to_add['song'] = chrome_browser.find_element_by_id('maintextlink').text
    tracks_to_return.append(track_to_add)
    return tracks_to_return

def scrape_spotify(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    song_json = json.loads(soup.find('script', {'id': 'resource'}).text)
    if 'tracks' in song_json.keys():
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
    else:
        print(f"no spotify tracks...")

def scrape_apple(url):
    tracks_to_return = []
    chrome_browser.get(url)
    try:
        element = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "name"))
        )
        element_two = WebDriverWait(chrome_browser, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "song__info__sub"))
        )
    except TimeoutException:
        print("Loading took too much time!")
    track_to_add = {
        'artist': chrome_browser.find_element_by_class_name('song__info__sub').get_property('title'),
        'song': chrome_browser.find_element_by_class_name('name').text
    }
    tracks_to_return.append(track_to_add)
    return tracks_to_return

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
        for blog in self.blog_list:
            print(f"gathering song links from: {blog}")
            page_links = []
            feed = feedparser.parse(blog[1])
            for entry in feed['entries']:
                if feed_to_feed_search[blog[0]].search(entry['title'].lower()):
                    page_links.append(entry['links'][0]['href'])

            print(f"found {len(page_links)} blog posts...")
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
            print(f"found {len(song_endpoints)} song links within {len(page_links)} blog posts...")
        return song_endpoints
    
    def get_song_data(self, song_list):
        song_data = []
        endpoints_with_domain = []
        for endpoint in song_list:
            soup = BeautifulSoup(requests.get(endpoint).text, 'html.parser')
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                if 'src' in iframe.attrs:
                    url_match = check_iframe_url(iframe['src'])
                    if url_match:
                        endpoints_with_domain.append((url_match.group(), iframe['src']))
        endpoints_with_domain = list(set(endpoints_with_domain))
        for endpoint in endpoints_with_domain:
            print(f"getting embed player track(s) data from: {endpoint[0]}")
            scrape_result = domain_to_scraper[endpoint[0]](endpoint[1])
            if scrape_result:
                song_data += scrape_result
        return song_data
