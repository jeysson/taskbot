from flask import Blueprint, render_template, request, redirect, url_for, session
from app.services.gmail_service import GmailService
import json
import os
import pickle

email_bp = Blueprint('email', __name__)
gmail_service = GmailService()

@email_bp.route('/emails', methods=['GET'])
def check_emails():
    redirect_uri = url_for('email.oauth2callback', _external=True)
    client_secret_path = os.path.join(os.path.dirname(__file__), '../../client_secret.json')
    try:
        client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET', '{}')
        client_secret = json.loads(client_secret_json) if client_secret_json else None
        if not client_secret and os.path.exists(client_secret_path):
            with open(client_secret_path, 'r') as f:
                client_secret = json.load(f)
        if not client_secret:
            raise ValueError("Nenhuma credencial válida encontrada em GOOGLE_CLIENT_SECRET ou client_secret.json")
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        return f"Erro ao carregar client_secret: {str(e)}", 500

    service, auth_redirect = gmail_service.get_service(session, redirect_uri, client_secret)
    if not service:
        return redirect(auth_redirect)
    gmail_service.check_emails(service)
    return "E-mails verificados!"

@email_bp.route('/oauth2callback')
def oauth2callback():
    redirect_uri = url_for('email.oauth2callback', _external=True)
    client_secret_path = os.path.join(os.path.dirname(__file__), '../../client_secret.json')
    try:
        client_secret_json = os.getenv('GOOGLE_CLIENT_SECRET', '{}')
        client_secret = json.loads(client_secret_json) if client_secret_json else None
        if not client_secret and os.path.exists(client_secret_path):
            with open(client_secret_path, 'r') as f:
                client_secret = json.load(f)
        if not client_secret:
            raise ValueError("Nenhuma credencial válida encontrada em GOOGLE_CLIENT_SECRET ou client_secret.json")
    except (json.JSONDecodeError, ValueError, FileNotFoundError) as e:
        return f"Erro ao carregar client_secret: {str(e)}", 500

    flow = gmail_service.gmail_model.authenticate(redirect_uri, client_secret)
    
    if 'code' not in request.args:
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        session['state'] = state
        return render_template('email/auth.html', auth_url=authorization_url)
    else:
        state = session.get('state')
        try:
            flow.fetch_token(code=request.args.get('code'), state=state)
            creds = flow.credentials
            with open('token.pickle', 'wb') as f:
                pickle.dump(creds, f)
            session['credentials'] = pickle.dumps(creds).decode('latin1')
            return render_template('email/auth_result.html', success=True)
        except Exception as e:
            error_message = f"Erro ao autenticar: {str(e)}"
            return render_template('email/auth_result.html', success=False, error_message=error_message)