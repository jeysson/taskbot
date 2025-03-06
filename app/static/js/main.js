console.log("TaskBot carregado!");

document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js não foi carregado corretamente.");
        return;
    }

    const canvas = document.getElementById('taskChart');
    if (canvas) {
        console.log("data-dates:", canvas.dataset.dates);
        console.log("data-counts:", canvas.dataset.counts);

        let dates, counts;
        const parseSafeJson = (data, fallback) => {
            if (!data || data === "") return fallback;
            try {
                return JSON.parse(data);
            } catch (e) {
                console.error("Erro ao parsear JSON:", e, "Dados:", data);
                return fallback;
            }
        };

        dates = parseSafeJson(canvas.dataset.dates, []);
        counts = parseSafeJson(canvas.dataset.counts, []);

        const ctx = canvas.getContext('2d');
        const taskChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Tarefas por Dia',
                    data: counts,
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