export function showPongChart(stats) {
	const ctx = document.getElementById('pongChart');
	if (ctx) {
		const pongChart = new Chart(ctx.getContext('2d'), {
			type: 'pie',
			data: {
				labels: ['Victories', 'Defeats'],
				datasets: [{
					label: 'Pong Stats',
					data: [stats.victories, stats.defeats],
					backgroundColor: [
						'rgba(0, 128, 0, 0.5)',
						'rgba(220, 53, 69, 0.5)'
					],
					borderColor: [
						'rgba(0, 128, 0, 1)',
						'rgba(220, 53, 69, 1)'
					],
					borderWidth: 1
				}]
			},
			options: {
				plugins: {
					legend: {
						position: 'left'
					}
				}
			}
		});
	} else {
		console.error('Element with ID "pongChart" not found.');
	}
}

export function showInvadersChart(stats) {
	const ctx = document.getElementById('invadersChart');
	if (ctx) {
		const invadersChart = new Chart(ctx.getContext('2d'), {
			type: 'line',
			data: {
				labels: stats.map((_, index) => `Game ${index + 1}`),
				datasets: [{
					label: 'Scores',
					data: stats,
					backgroundColor: 'rgba(75, 192, 192, 0.2)',
					borderColor: 'rgba(75, 192, 192, 1)',
					borderWidth: 1,
					fill: false
				}]
			},
			options: {
				scales: {
					y: {
						beginAtZero: true
					}
				}
			}
		});
	} else {
		console.error('Element with ID "invadersChart" not found.');
	}
}
