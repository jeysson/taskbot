console.log("TaskBot carregado!");

document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js não foi carregado corretamente.");
        return;
    }

    const canvas = document.getElementById('taskChart');
    if (canvas) {
        const taskCount = parseInt(canvas.dataset.taskCount) || 0;  // Converte para inteiro, padrão 0 se inválido

        const ctx = canvas.getContext('2d');
        const taskChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Tarefas Processadas'],
                datasets: [{
                    label: 'Quantidade',
                    data: [taskCount],
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    }
});