from app.models.sheets import Sheets

class SheetsService:
    def __init__(self):
        self.sheets_model = Sheets()

    def append_data(self, data):
        self.sheets_model.append_row(data)