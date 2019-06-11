from music_scraper import ScrapeSession
from gmusic_api import GmSession
import time

scraping = ScrapeSession()
song_links = scraping.get_song_links()
song_data_list = scraping.get_song_data(song_links)

session = GmSession()
session.login()

nid_list = []
for track in song_data_list:
    print(f'gathering: {track}')
    time.sleep(1)
    result = session.search(track['artist'], track['song'])
    if result:
        nid_list.append(result)
session.add_to_playlist(nid_list)

session.logout()