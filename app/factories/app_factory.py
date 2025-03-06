from flask import Flask, render_template
from app.config import Config
from app.routes.task_routes import task_bp
from app.routes.email_routes import email_bp
import os

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
                static_folder=os.path.join(os.path.dirname(__file__), '../static'))
    app.config.from_object(Config)
    
    # Registrar Blueprints
    app.register_blueprint(task_bp, url_prefix='/task')
    app.register_blueprint(email_bp, url_prefix='/email')
    
    @app.route('/')
    def home():
        return render_template('base.html')
    
    return app