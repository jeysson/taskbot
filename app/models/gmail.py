from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
import pickle
import base64
import sqlite3
from requests import Request
from app.factories.db_factory import ensure_db

class Gmail:
    def __init__(self):
        self.scope = [
            "https://www.googleapis.com/auth/gmail.modify",
            "https://www.googleapis.com/auth/drive",
            "https://www.googleapis.com/auth/spreadsheets"
        ]
        self.db_path = ensure_db('taskbot.db')  # Garante que o banco exista

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
        else:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT token FROM tokens WHERE service = 'gmail'")
            token_data = c.fetchone()
            conn.close()
            if token_data:
                try:
                    creds = pickle.loads(token_data[0])
                except (pickle.PickleError, EOFError):
                    creds = None
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            self.save_credentials(creds)
        return creds

    def save_credentials(self, creds):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO tokens (service, token) VALUES ('gmail', ?)",
                  (pickle.dumps(creds),))
        conn.commit()
        conn.close()