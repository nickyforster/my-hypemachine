from music_scraper import ScrapeSession
from gmusic_api import GmSession
test = {'artist': 'Havelock', 'song': 'Vacancy'}

scraping = ScrapeSession()
song_links = scraping.get_song_links()
scraping.get_song_data(song_links)
# session = GmSession()
# session.login()
# session.search(test['artist'], test['song'])
# session.logout()