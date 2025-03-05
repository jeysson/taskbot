from flask import Flask, render_template, request
import pdfplumber
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# Configuração Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name('taskbot-service-account.json', SCOPE)
CLIENT = gspread.authorize(CREDS)
SHEET = CLIENT.open("TaskBot Data").sheet1

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            # Salvar temporariamente
            file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(file_path)
            
            # Extrair dados
            with pdfplumber.open(file_path) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()
                # Exemplo simples: extrair nome, data, valor (ajuste conforme seu PDF)
                lines = text.split('\n')
                data = {
                    'nome': lines[0] if lines else 'N/A',
                    'data': next((l for l in lines if '/' in l or '-' in l), 'N/A'),
                    'valor': next((l for l in lines if '$' in l or 'R$' in l), 'N/A')
                }
            
            # Enviar para Google Sheets
            SHEET.append_row([data['nome'], data['data'], data['valor']])
            
            # Remover arquivo temporário
            os.remove(file_path)
            return f"Dados extraídos e enviados: {data}"
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)