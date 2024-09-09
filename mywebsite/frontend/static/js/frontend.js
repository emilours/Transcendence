import { initializeGame } from '/static/js/invaders.js';

document.addEventListener("DOMContentLoaded", () => {
	// Font size adjustment
	const increaseFontBtn = document.getElementById('increase-font');
	const decreaseFontBtn = document.getElementById('decrease-font');
	const rootElement = document.documentElement;
	let currentFontSize = 100;

	increaseFontBtn.addEventListener('click', function() {
		if (currentFontSize < 150) {
			currentFontSize += 10;
			rootElement.style.fontSize = currentFontSize + '%';
		}
	});

	decreaseFontBtn.addEventListener('click', function() {
		if (currentFontSize > 50) {
			currentFontSize -= 10;
			rootElement.style.fontSize = currentFontSize + '%';
		}
	});

	// Manage alerts
	function showAlert(message) {
		const alertContainer = document.getElementById('alert-container');
		const alertMessage = document.getElementById('alert-message');

		alertMessage.textContent = message;
		alertContainer.classList.remove('d-none');
	}

	function closeAlert() {
		document.getElementById('alert-container').classList.add('d-none');
	}

	// SPA - Single Page Application
	const app = document.getElementById('app');

	const loadResource = (url, type) => {
		return new Promise((resolve, reject) => {
			const element = document.createElement(type);
			if (type === 'script')
				element.type = "module";
			if (type === 'link')
				element.rel = "stylesheet";
			element.href = element.src = url
			element.onload = resolve;
			element.onerror = reject;
			element.dataset.dynamic = true;
			document.head.appendChild(element);
		});
	};

	const loadHeader = async () => {
		try {
			const response = await fetch('/load_header/', {
				headers: {
					'X-Requested-With': 'XMLHttpRequest'
				}
			});
			const data = await response.json();
			const headerElement = document.querySelector('header');
			headerElement.innerHTML = data.html;
		} catch (error) {
			console.error('Error loading header:', error);
		}
	};


	const loadContent = async (url, addToHistory = true) => {
		try {
			const response = await fetch(url, {
				headers: {
					'X-Requested-With': 'XMLHttpRequest'
				}
			});
			if (!response.ok) throw new Error('Network response was not ok');
			const data = await response.json();
			app.innerHTML = data.html;

			if (url.includes('invaders')) {
				await loadResource('https://cdn.jsdelivr.net/npm/gifler@0.1.0/gifler.min.js', 'script');
				await loadResource('/static/css/invaders.css', 'link');
				await loadResource('/static/js/invaders.js', 'script');
				await initializeGame();
			} else if (url.includes('pong')) {
				await loadResource('/static/js/pong.js', 'script');
			}

			attachListeners();

			if (addToHistory) history.pushState({ route: url }, null, url);
		} catch (error) {
			console.error('Error loading content:', error);
		}
	};

	const attachListeners = () => {
		const links = [
			{ id: 'home', url: '/home/' },
			{ id: 'login-from-signup', url: '/login/' },
			{ id: 'login-from-home', url: '/login/' },
			{ id: 'signup-from-login', url: '/signup/' },
			{ id: 'navbar-signup', url: '/signup/' },
			{ id: 'navbar-login', url: '/login/' },
			{ id: 'navbar-profile', url: '/profile/' },
			{ id: 'navbar-leaderboard', url: '/leaderboard/' },
			{ id: 'games', url: '/games/' },
			{ id: 'invaders', url: '/invaders/' },
			{ id: 'pong', url: '/pong/' }
		];

		links.forEach(link => {
			const element = document.getElementById(link.id);
			if (element) {
				element.addEventListener('click', event => {
					event.preventDefault();
					loadContent(link.url);
				});
			}
		});

		const forms = [
			{ id: 'signup-form', url: '/auth/signup/' },
			{ id: 'login-form', url: '/auth/signin/' },
			{ id: 'logout-form', url: '/auth/signout/' },
			{ id: 'add-friend-form', url: '/auth/send_friend_request/' }
		];

		forms.forEach(({ id, url }) => {
			const form = document.getElementById(id);
			if (form) {
				form.addEventListener('submit', async (event) => {
					event.preventDefault();
					const formData = new FormData(form);
					try {
						const response = await fetch(url, {
							method: 'POST',
							body: formData,
							headers: {
								'X-Requested-With': 'XMLHttpRequest',
								"X-CSRFToken": getCookie('csrftoken')
							},
						});
						const data = await response.json();
						if (data.error) {
							alert(data.error);
						} else {
							// alert(data.message);
							if (id === 'logout-form') {
								// window.location.href = '/home/';
								loadHeader();
								loadContent('/home/', true);
							} else {
								// window.location.href = '/profile/';
								loadContent('/profile/', true);
								loadHeader();
							}
						}
					} catch (error) {
						console.error('Error:', error);
					}
				});
			}
		});

		document.querySelectorAll('.accept-friend-request, .refuse-friend-request, .cancel-friend-request, .remove-friend-form').forEach(form => {
			form.addEventListener('submit', async (event) => {
				event.preventDefault();

				const formData = new FormData(form);
				const url = form.action;

				try {
					const response = await fetch(url, {
						method: 'POST',
						body: formData,
						headers: {
							'X-Requested-With': 'XMLHttpRequest',
							"X-CSRFToken": getCookie('csrftoken')
						},
					});

					const data = await response.json();
					if (data.error) {
						alert(data.error);
					} else {
						// alert(data.message);
						loadContent('/profile/', true);
					}
				} catch (error) {
					console.error('Error:', error);
				}
			});
		});
	};

	function getCookie(name) {
		let cookieValue = null;
		if (document.cookie && document.cookie !== '') {
			const cookies = document.cookie.split(';');
			for (let i = 0; i < cookies.length; i++) {
				const cookie = cookies[i].trim();
				if (cookie.substring(0, name.length + 1) === (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
		return cookieValue;
	}

	// const getCookie = (name) => {
	//     const cookies = document.cookie.split(';').map(cookie => cookie.trim());
	//     const match = cookies.find(cookie => cookie.startsWith(`${name}=`));
	//     return match ? decodeURIComponent(match.split('=')[1]) : null;
	// };

	window.addEventListener('popstate', () => loadContent(window.location.pathname, false));
	loadContent(window.location.pathname, false);
});
