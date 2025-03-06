from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
import pickle
import base64
from requests import Request

class Gmail:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        self.token_file = 'token.pickle'

    def authenticate(self, redirect_uri, client_secret):
        flow = Flow.from_client_config(client_secret, scopes=self.scope, redirect_uri=redirect_uri)
        return flow

    def load_credentials(self, session):
        creds = None
        token_base64 = os.getenv('GMAIL_TOKEN')
        if token_base64 and not session.get('credentials'):
            try:
                creds = pickle.loads(base64.b64decode(token_base64))
            except (pickle.PickleError, base64.binascii.Error):
                creds = None
        elif os.path.exists(self.token_file) and os.path.getsize(self.token_file) > 0:
            try:
                with open(self.token_file, 'rb') as f:
                    creds = pickle.load(f)
            except (pickle.PickleError, EOFError):
                creds = None
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(self.token_file, 'wb') as f:
                pickle.dump(creds, f)
        return creds