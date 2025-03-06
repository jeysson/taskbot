from flask import Blueprint, render_template, request
from app.services.task_service import TaskService

task_bp = Blueprint('task', __name__)
task_service = TaskService()

@task_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    result = None
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            data = task_service.process_pdf(file)
            result = f"Dados extraídos e enviados: {data}"
    return render_template('task/upload.html', result=result)

@task_bp.route('/dashboard')
def dashboard():
    tasks, task_count, time_saved = task_service.get_dashboard_data()
    return render_template('task/dashboard.html', tasks=tasks, task_count=task_count, time_saved=time_saved)