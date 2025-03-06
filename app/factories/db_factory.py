import sqlite3
import os

def ensure_db(db_path='taskbot.db'):
    """Cria o arquivo taskbot.db e suas tabelas se não existirem."""
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                     (id INTEGER PRIMARY KEY, type TEXT, timestamp TEXT, data TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS tokens 
                     (id INTEGER PRIMARY KEY, service TEXT UNIQUE, token BLOB)''')
        conn.commit()
        conn.close()
    return db_path