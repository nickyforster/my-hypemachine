from gmusicapi import Mobileclient
from gmusic_config import gmusic_cred_path,gmusic_device_id

class GmSession:
    def __init__(self, device_id, cred_path):
        self.session = Mobileclient()
        self.device_id = device_id
        self.cred_path = cred_path

    def login(self):
        self.session.oauth_login(device_id=self.device_id, oauth_credentials=self.cred_path)

    def logout(self):
        self.session.logout()

session = GmSession(gmusic_device_id, gmusic_cred_path)
session.login()
session.logout()