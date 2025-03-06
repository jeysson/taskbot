from flask import Flask, render_template, request, redirect, url_for, session, Response
import pdfplumber
import gspread
from google.oauth2.service_account import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import os
import json
import sqlite3
import datetime
import base64
import pickle

app = Flask(__name__)
app.secret_key = 'sua-chave-secreta-aqui'  # Substitua por algo único e seguro

# Configuração Google APIs
SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",  # Atualizado
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/gmail.modify"
]

# Google Sheets (Service Account)
creds_json = os.getenv('GOOGLE_CREDENTIALS', '{}')
if creds_json:
    SHEET_CREDS = Credentials.from_service_account_info(json.loads(creds_json), scopes=SCOPE)
else:
    SHEET_CREDS = Credentials.from_service_account_file('taskbot-service-account.json', scopes=SCOPE)
SHEET_CLIENT = gspread.authorize(SHEET_CREDS)
SHEET = SHEET_CLIENT.open("TaskBot Data").sheet1

# Gmail (OAuth 2.0)
def get_gmail_service():
    if 'credentials' not in session:
        token_base64 = os.getenv('GMAIL_TOKEN')
        if token_base64:
            creds = pickle.loads(base64.b64decode(token_base64))
            if creds.valid:
                session['credentials'] = pickle.dumps(creds).decode('latin1')
                return build('gmail', 'v1', credentials=creds)
        return redirect(url_for('oauth2callback'))
    creds = pickle.loads(session['credentials'].encode('latin1'))
    if not creds.valid:
        return redirect(url_for('oauth2callback'))
    return build('gmail', 'v1', credentials=creds)

@app.route('/oauth2callback')
def oauth2callback():
    redirect_uri = url_for('oauth2callback', _external=True)
    creds_json = os.getenv('GOOGLE_CLIENT_SECRET', '{}')
    if creds_json:
        flow = Flow.from_client_config(
            json.loads(creds_json),
            scopes=SCOPE,
            redirect_uri=redirect_uri
        )
    else:
        flow = Flow.from_client_secrets_file(
            'client_secret.json',
            scopes=SCOPE,
            redirect_uri=redirect_uri
        )
    
    if 'code' not in request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['state'] = state
        print(f"Por favor, visite este URL para autorizar: {authorization_url}")
        return "Verifique o terminal para o URL de autorização."
    else:
        state = session.get('state')
        flow.fetch_token(code=request.args.get('code'), state=state)
        session['credentials'] = pickle.dumps(flow.credentials).decode('latin1')
        return redirect(url_for('home'))

# Configuração SQLite
def init_db():
    conn = sqlite3.connect('taskbot.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, type TEXT, timestamp TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            with pdfplumber.open(file_path) as pdf:
                page = pdf.pages[0]
                text = page.extract_text() or ""
                lines = text.split('\n')
                data = {
                    'nome': lines[0] if lines else 'N/A',
                    'data': next((l for l in lines if '/' in l or '-' in l), 'N/A'),
                    'valor': next((l for l in lines if '$' in l or 'R$' in l), 'N/A')
                }
            
            SHEET.append_row([data['nome'], data['data'], data['valor']])
            
            conn = sqlite3.connect('taskbot.db')
            c = conn.cursor()
            c.execute("INSERT INTO tasks (type, timestamp, data) VALUES (?, ?, ?)",
                     ('upload', datetime.datetime.now().isoformat(), str(data)))
            conn.commit()
            conn.close()
            
            os.remove(file_path)
            return f"Dados extraídos e enviados: {data}"
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('taskbot.db')
    c = conn.cursor()
    c.execute("SELECT type, timestamp, data FROM tasks")
    tasks = c.fetchall()
    conn.close()
    task_count = len(tasks)
    time_saved = task_count * 0.1
    return render_template('dashboard.html', tasks=tasks, task_count=task_count, time_saved=time_saved)

@app.route('/emails', methods=['GET'])
def check_emails():
    gmail_service = get_gmail_service()
    if isinstance(gmail_service, Response):  # Redirecionamento para login
        return gmail_service
    results = gmail_service.users().messages().list(userId='me', q='status').execute()
    messages = results.get('messages', [])
    
    for msg in messages[:5]:
        msg_data = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']
        sender = next(h['value'] for h in headers if h['name'] == 'From')
        snippet = msg_data['snippet']
        if 'status' in snippet.lower():
            response = {
                'raw': base64.urlsafe_b64encode(
                    f"From: TaskBot\nTo: {sender}\nSubject: Re: Status\n\nEm processamento.".encode()
                ).decode()
            }
            gmail_service.users().messages().send(userId='me', body=response).execute()
    return "E-mails verificados!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)