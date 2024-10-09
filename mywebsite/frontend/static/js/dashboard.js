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
					hoverBackgroundColor: [
						'rgba(0, 128, 0, 1)',
						'rgba(220, 53, 69, 1)'
					],
					borderColor: [
						'rgba(83, 53, 35, 0.8)',
						'rgba(83, 53, 35, 0.8)'
					],
					borderWidth: 2
				}]
			},
			options: {
				plugins: {
					legend: {
						position: 'left',
						labels: {
							color: 'rgba(83, 53, 35, 0.7)'
						}
					},
					tooltip: {
						backgroundColor: 'rgba(83, 53, 35, 0.9)'
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
					backgroundColor: 'rgba(255, 235, 234, 1)',
					hoverBackgroundColor: 'rgba(255, 167, 200, 1)',
					borderColor: 'rgba(83, 53, 35, 0.8)',
					borderWidth: 2,
					fill: false,
					pointRadius: 5,
					hoverRadius: 10,
					hoverBorderWidth: 3
				}]
			},
			options: {
				scales: {
					y: {
						beginAtZero: true,
						ticks: {
							color: 'rgba(83, 53, 35, 0.7)'
						}
					},
					x: {
						ticks: {
							color: 'rgba(83, 53, 35, 0.7)'
						}
					}
				},
				plugins: {
					legend: {
						labels: {
							color: 'rgba(83, 53, 35, 0.7)'
						}
					},
					tooltip: {
						backgroundColor: 'rgba(83, 53, 35, 0.9)'
					}
				}
			}
		});
	} else {
		console.error('Element with ID "invadersChart" not found.');
	}
}
