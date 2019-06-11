from gmusicapi import Mobileclient
from gmusic_config import gmusic_cred_path,gmusic_device_id,gmusic_playlist_id

class GmSession:
    def __init__(self):
        self.session = Mobileclient()
        self.device_id = gmusic_device_id
        self.cred_path = gmusic_cred_path
        self.playlist_id = gmusic_playlist_id

    def login(self):
        self.session.oauth_login(device_id=self.device_id, oauth_credentials=self.cred_path)

    def logout(self):
        self.session.logout()
    
    def search(self, artist, song):
        search_string = f'{artist.lower()}' + f', {song.lower()}'
        results = self.session.search(search_string, max_results=20)
        if len(results['song_hits']) > 0:
            first_result = results['song_hits'][0]['track']
            if 'storeId' in first_result.keys():
                return first_result['storeId']
            elif 'id' in first_result.keys():
                print('bad id')
                return first_result['id']
            elif 'nid' in first_result.keys():
                print('bad id')
                return results['song_hits'][0]['track']['nid']
        else:
            print('No songs found...')
    
    def add_to_playlist(self, song_list):
        playlists = self.session.get_all_user_playlist_contents()
        for playlist in playlists:
            if playlist['id'] == self.playlist_id:
                to_remove = []
                for track in playlist['tracks']:
                    to_remove.append(track['id'])

                print('Adding new songs...')
                res = self.session.add_songs_to_playlist(self.playlist_id, song_list)
                print('Removing previous songs...')
                out = self.session.remove_entries_from_playlist(to_remove)
                print('Finished')



        