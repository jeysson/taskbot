import os

class Config:
    SECRET_KEY = 'sua-chave-secreta-aqui'  # Substitua por uma chave segura
    GOOGLE_CREDENTIALS = os.getenv('GOOGLE_CREDENTIALS')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GMAIL_TOKEN = os.getenv('GMAIL_TOKEN')
    PORT = int(os.getenv('PORT', 8080))