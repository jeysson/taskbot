from flask import Blueprint, render_template, request
from app.services.task_service import TaskService
from collections import Counter
from datetime import datetime
import json

task_bp = Blueprint('task', __name__)
task_service = TaskService()

@task_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    error = None
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            error = "Nenhum arquivo selecionado."
        elif not file.filename.endswith('.pdf'):
            error = "Apenas arquivos PDF são suportados."
        else:
            try:
                data = task_service.process_pdf(file)
                return render_template('task/success.html', message=f"Dados extraídos e enviados: {data}")
            except Exception as e:
                error = f"Erro ao processar o PDF: {str(e)}"
    return render_template('task/upload.html', error=error)

@task_bp.route('/dashboard')
def dashboard():
    tasks, task_count, time_saved = task_service.get_dashboard_data()
    task_dates = [datetime.fromisoformat(task[1]).date().isoformat() for task in tasks] if tasks else []
    tasks_by_day = Counter(task_dates)
    dates = list(tasks_by_day.keys()) if tasks_by_day else []
    counts = list(tasks_by_day.values()) if tasks_by_day else []
    dates_json = json.dumps(dates)
    counts_json = json.dumps(counts)
    return render_template('task/dashboard.html', tasks=tasks, task_count=task_count, time_saved=time_saved, dates_json=dates_json, counts_json=counts_json)