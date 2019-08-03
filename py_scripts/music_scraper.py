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

blog_to_feed_search = {
    'largeheartedboy': re.compile(r'^shorties.*$'),
    'killing-moon': re.compile(r'^totd.*$'),
    'earmilk': re.compile(r'new\s[(song|ep|album)]')
}

blog_to_second_level_search = {
    'largeheartedboy': re.compile('^stream'),
}

## Killing-moon has page links that lead to pages with the iframe in them.
## Largehearted boy has page links that lead to pages with the more links with iframes in them.
## Earmilk has page links that lead to pages with the iframe in them.
def extract_page_links_from_feed(blog):
    blog_name = blog[0]
    blog_url = blog[1]
    blog_levels = blog[2]

    entry_match = blog_to_feed_search[blog_name]
    feed = feedparser.parse(blog_url)

    entries = feed['entries']
    page_links = []
    for entry in entries:
        if entry_match.search(entry['title'].lower()):
            page_links.append(entry['links'][0]['href'])

    if blog_levels == 1:
        return page_links
    
    elif blog_levels == 2:
        real_links = []
        for link in page_links:
            second_level_search = blog_to_second_level_search[blog_name]
            soup = BeautifulSoup(requests.get(link).text, 'html.parser')
            content_links = soup.find_all('a')
            for content_link in content_links:
                test_text = content_link.find_parent('p')
                if test_text:
                    if second_level_search.search(test_text.text.lower()):
                        real_links.append(content_link['href'])
        return real_links

# def scrape_earmilk_for_iframe_links(blog):
#     entry_match = re.compile(r'.*')
#     feed = feedparser.parse(blog[1])
#     page_links = []
#     for entry in feed['entries']:
#         for tag in entry['tags']:
#             if tag['term'] == 'New Music Friday':
#                 page_links.append(entry['links'][0]['href'])
#                 break
#     return page_links


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
    print(soundcloud_title)
    ## We can't count on "by", even though it's the most frequent
    split_title = soundcloud_title.split('by')
    if len(split_title) > 1:
        track = soundcloud_title.split('by')[0].strip()
        artist = soundcloud_title.split('by')[1].strip()
        track_to_add = {
            'artist': artist,
            'song': track
        }

        tracks_to_return.append(track_to_add)
    else:
        print(f"no 'by' in this title: {soundcloud_title}")
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
            # ('largeheartedboy','http://feeds.feedburner.com/largeheartedboy',2),
            # ('killing-moon','http://www.killing-moon.com/feed',1),
            ('earmilk','https://earmilk.com/feed/',1)
        ]
    
    def get_song_links_from_feed(self):
        endpoints_with_domain = []
        for blog in self.blog_list:
            print(f"gathering song links from: {blog}")
            song_endpoints = extract_page_links_from_feed(blog)

            print(f"found {len(song_endpoints)} song links...")

            for endpoint in song_endpoints:
                soup = BeautifulSoup(requests.get(endpoint).text, 'html.parser')
                iframes = soup.find_all('iframe')
                for iframe in iframes:
                    if 'src' in iframe.attrs:
                        url_match = check_iframe_url(iframe['src'])
                        if url_match:
                            endpoints_with_domain.append((blog[0], url_match.group(), iframe['src']))
        endpoints_with_domain = list(set(endpoints_with_domain))
        
        print(endpoints_with_domain)
        return endpoints_with_domain
    
    def get_song_data(self, song_list):
        ## The song list has a bunch of iframe endpoints
        ## Some endpoints have many iframes
        ## Need to add a step for iframe selection
        song_data = []
        for endpoint in song_list:
            print(endpoint[2])
            print(f"getting embed player track(s) data from: {endpoint[1]}")
            scrape_result = domain_to_scraper[endpoint[1]](endpoint[2])
            if scrape_result:
                song_data += scrape_result
        return song_data
