from gmusicapi import Mobileclient
from gmusic_config import gmusic_cred_path,gmusic_device_id

class GmSession:
    def __init__(self):
        self.session = Mobileclient()
        self.device_id = gmusic_device_id
        self.cred_path = gmusic_cred_path

    def login(self):
        self.session.oauth_login(device_id=self.device_id, oauth_credentials=self.cred_path)

    def logout(self):
        self.session.logout()
    
    def search(self, artist, song):
        search_string = f'{artist.lower()}' + f', {song.lower()}'
        results = self.session.search(search_string, max_results=20)
        if len(results['song_hits']) > 0:
            return results['song_hits'][0]['nid']
        else:
            print('No songs found...')
        