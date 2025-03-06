import sqlite3

def init_db(db_path='taskbot.db'):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks 
                 (id INTEGER PRIMARY KEY, type TEXT, timestamp TEXT, data TEXT)''')
    conn.commit()
    conn.close()
    return db_path