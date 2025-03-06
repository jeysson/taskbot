import os
from app.factories.app_factory import create_app
from app.factories.db_factory import ensure_db

# Garante que o banco exista antes de iniciar o app
ensure_db()

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'])