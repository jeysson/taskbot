import gspread
from google.oauth2.service_account import Credentials
import os
import json

class Sheets:
    def __init__(self):
        self.scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds_json = os.getenv('GOOGLE_CREDENTIALS', '{}')
        if creds_json:
            self.creds = Credentials.from_service_account_info(json.loads(creds_json), scopes=self.scope)
        else:
            self.creds = Credentials.from_service_account_file('taskbot-service-account.json', scopes=self.scope)
        self.client = gspread.authorize(self.creds)
        self.sheet = self.client.open("TaskBot Data").sheet1

    def append_row(self, data):
        self.sheet.append_row(data)