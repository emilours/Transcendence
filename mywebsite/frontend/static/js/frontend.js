import { startInvaders, stopInvaders } from '/static/js/invaders.js';
import { initPong } from '/static/js/pongMenu.js';
import { CloseWebsocket } from '/static/js/pong.js';
import { showPongChart, showInvadersChart } from '/static/js/dashboard.js';

document.addEventListener("DOMContentLoaded", () => {
	// SSE - Server-Sent Events
	let eventSource = null;
	function initSSE() {
		if (eventSource === null || eventSource.readyState === EventSource.CLOSED) {
			eventSource = new EventSource('/auth/sse/');

			eventSource.onmessage = function(event) {
				const data = JSON.parse(event.data);
				if (data && (data.friend_requests || data.friend_count >= 0)) {
					if (window.location.pathname === '/profile/') {
						loadContent('/profile/', false);
					}
				}
			};

			eventSource.onerror = function(error) {
				console.error('EventSource error:', error);
				eventSource.close();
				setTimeout(function() {
					eventSource = new EventSource('/auth/sse/');
				}, 5000);
			};

			console.log('SSE connection initialized');
		} else {
			console.log('SSE connection already active');
		}
	}

	function checkLoginStatus() {
		return localStorage.getItem('isLoggedIn') === 'true';
	}

	if (checkLoginStatus()) {
		console.log('User is logged in. Initiating SSE after refresh...');
		initSSE();
	}

	// SPA - Single Page Application
	const app = document.getElementById('app');

	const loadResource = (url, type) => {
		return new Promise((resolve, reject) => {
			const element = document.createElement(type);
			if (type === 'script') {
				element.type = "module";
				element.src = url;
 			} else if (type === 'link') {
				 element.rel = "stylesheet";
				 element.href = element.src = url
			}
			element.onload = resolve;
			element.onerror = reject;
			element.dataset.dynamic = true;
			document.head.appendChild(element);
		});
	};

	function cleanupResources() {
		document.querySelectorAll('script[data-dynamic="true"]').forEach(script => script.remove());
		document.querySelectorAll('link[data-dynamic="true"]').forEach(link => link.remove());
		// close ws connection and cleanup threejsz
		CloseWebsocket();
		stopInvaders();

		// Close any open Bootstrap modals
		const modals = document.querySelectorAll('.modal.show');
		modals.forEach(modal => {
			const modalInstance = bootstrap.Modal.getInstance(modal);
			if (modalInstance) {
				modalInstance.hide();
			}
		});
	}

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
			attachNavListeners();
		} catch (error) {
			console.error('Error loading header:', error);
		}
	};


	const loadContent = async (url, addToHistory = true) => {
		cleanupResources();
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
				await startInvaders(data.test_name);
			} else if (url.includes('pong')) {
				await loadResource('https://cdn.jsdelivr.net/Failed to load resource: the server responded with a status of 404 (Not Found)/gifler@0.1.0/gifler.min.js', 'script');
				await loadResource('/static/css/pong.css', 'link');
				await loadResource('/static/js/pongMenu.js', 'script');
				await initPong(data.test_name);
			} else if (url.includes('dashboard')) {
				await loadResource('/static/js/dashboard.js', 'script');
				await console.log('pong_stats:', data.pong_stats);
				await showPongChart(data.pong_stats);
				await showInvadersChart(data.invaders_stats.last_five_scores);
			} else if (url.includes('signup')) {
				attachPolicyListeners();
			} else if (url.includes('profile')) {
				if (!checkLoginStatus()) {
					localStorage.setItem('isLoggedIn', 'true');
					initSSE();
				}
			}
			attachListeners();
			if (addToHistory) history.pushState({ route: url }, null, url);
		} catch (error) {
			console.error('Error loading content:', error);
		}
	};

	const attachNavListeners = () => {
		// Accessibility features
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

		const toggleContrastBtn = document.getElementById('toggle-contrast');
		let isHighContrast = localStorage.getItem('highContrast') === 'true';

		toggleContrastBtn.addEventListener('click', function () {
			document.body.classList.toggle('high-contrast');
			isHighContrast = !isHighContrast;
			localStorage.setItem('highContrast', isHighContrast);
		});

		// Navbar links
		const NavLinks = [
			{ id: 'navbar-home', url: '/home/' },
			{ id: 'navbar-login', url: '/login/' },
			{ id: 'navbar-signup', url: '/signup/' },
			{ id: 'navbar-profile', url: '/profile/' },
			{ id: 'navbar-leaderboard', url: '/leaderboard/' },
			{ id: 'navbar-games', url: '/games/' },
			{ id: 'navbar-contact', url: '/contact/' },
		];

		NavLinks.forEach(link => {
			const element = document.getElementById(link.id);
			if (element) {
				element.addEventListener('click', event => {
					event.preventDefault();
					loadContent(link.url);
				});
			}
		});
	};

	const attachListeners = () => {
		// Attach listeners to links and forms
		const links = [
			{ id: 'login-from-signup', url: '/login/' },
			{ id: 'login-from-home', url: '/login/' },
			{ id: 'games-from-home', url: '/games/' },
			{ id: 'signup-from-login', url: '/signup/' },
			{ id: 'home-from-deleted', url: '/home/' },
			{ id: 'edit-profile', url: '/edit_profile/' },
			{ id: 'edit-password', url: '/edit_password/' },
			{ id: 'dashboard', url: '/dashboard/' },
			{ id: 'login-from-games', url: '/login/' },
			{ id: 'invaders', url: '/invaders/' },
			{ id: 'pong', url: '/pong/' },
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
			{ id: 'add-friend-form', url: '/auth/send_friend_request/' },
			{ id: 'edit-profile-form', url: '/auth/update_profile/' },
			{ id: 'edit-password-form', url: '/auth/update_password/' },
			{ id: 'delete-account-form', url: '/auth/delete_profile/' },
			{ id: 'anonymize-data-form', url: '/auth/request_anonymization/' },
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
						if (data.errors) {
							let errorMessage = '';
							for (const [field, messages] of Object.entries(data.errors)) {
								errorMessage += `${messages.join(', ')}\n`;
							}
							alert(errorMessage);
						} else if (data.error) {
							alert(data.error);
						} else {
							// alert(data.message);
							if (id === 'logout-form') {
								localStorage.removeItem('isLoggedIn');
								if (eventSource) {
									eventSource.close();
									console.log('SSE connection closed');
								}
								loadContent('/home/', true);
								loadHeader();
							} else if (id === 'delete-account-form') {
								loadContent('/deleted_profile/', true);
								loadHeader();
							} else if (id === 'signup-form' || id === 'login-form' || id === 'edit-profile-form' || id === 'anonymize-data-form') {
								loadContent('/profile/', true);
								loadHeader();
							} else {
								loadContent('/profile/', true);
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

	const attachPolicyListeners = () => {
		const privacyPolicyLink = document.getElementById('privacyPolicyLink');
		const privacyPolicyModal = new bootstrap.Modal(document.getElementById('privacyPolicyModal'));

		if (privacyPolicyLink) {
			privacyPolicyLink.addEventListener('click', (event) => {
				event.preventDefault();
				privacyPolicyModal.show();
			});
		}
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

	window.addEventListener('popstate', () => loadContent(window.location.pathname, false));

	loadContent(window.location.pathname, false);
	loadHeader();
});

	// // Manage alerts
	// function showAlert(message) {
	// 	const alertContainer = document.getElementById('alert-container');
	// 	const alertMessage = document.getElementById('alert-message');

	// 	alertMessage.textContent = message;
	// 	alertContainer.classList.remove('d-none');
	// }

	// function closeAlert() {
	// 	document.getElementById('alert-container').classList.add('d-none');
	// }
