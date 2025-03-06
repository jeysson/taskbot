from app.models.gmail import Gmail
from googleapiclient.discovery import build
import base64
import pickle  # Adicionado o import

class GmailService:
    def __init__(self):
        self.gmail_model = Gmail()

    def get_service(self, session, redirect_uri, client_secret):
        creds = self.gmail_model.load_credentials(session)
        if not creds or not creds.valid:
            return None, redirect_uri
        session['credentials'] = pickle.dumps(creds).decode('latin1')
        return build('gmail', 'v1', credentials=creds), None

    def check_emails(self, service):
        results = service.users().messages().list(userId='me', q='status').execute()
        messages = results.get('messages', [])
        for msg in messages[:5]:
            msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = msg_data['payload']['headers']
            sender = next(h['value'] for h in headers if h['name'] == 'From')
            snippet = msg_data['snippet']
            if 'status' in snippet.lower():
                response = {
                    'raw': base64.urlsafe_b64encode(
                        f"From: TaskBot\nTo: {sender}\nSubject: Re: Status\n\nEm processamento.".encode()
                    ).decode()
                }
                service.users().messages().send(userId='me', body=response).execute()
        return True