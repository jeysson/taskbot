from app.models.task import Task
from app.models.sheets import Sheets
import pdfplumber
import os

class TaskService:
    def __init__(self):
        self.task_model = Task()
        self.sheets_model = Sheets()

    def process_pdf(self, file):
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
        
        self.sheets_model.append_row([data['nome'], data['data'], data['valor']])
        self.task_model.add_task('upload', data)
        os.remove(file_path)
        return data

    def get_dashboard_data(self):
        tasks = self.task_model.get_tasks()
        task_count = len(tasks)
        time_saved = task_count * 0.1
        return tasks, task_count, time_saved