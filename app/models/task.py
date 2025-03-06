import sqlite3
import datetime

class Task:
    def __init__(self, db_path='taskbot.db'):
        self.db_path = db_path

    def add_task(self, task_type, data):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO tasks (type, timestamp, data) VALUES (?, ?, ?)",
                 (task_type, datetime.datetime.now().isoformat(), str(data)))
        conn.commit()
        conn.close()

    def get_tasks(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT type, timestamp, data FROM tasks")
        tasks = c.fetchall()
        conn.close()
        return tasks