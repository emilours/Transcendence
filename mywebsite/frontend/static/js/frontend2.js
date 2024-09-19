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

	const toggleContrastBtn = document.getElementById('toggle-contrast');
	let isHighContrast = localStorage.getItem('highContrast') === 'true';

	toggleContrastBtn.addEventListener('click', function () {
		document.body.classList.toggle('high-contrast');
		isHighContrast = !isHighContrast;
		localStorage.setItem('highContrast', isHighContrast);
	});


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

	function cleanupResources() {
		document.querySelectorAll('script[data-dynamic="true"]').forEach(script => script.remove());
		document.querySelectorAll('link[data-dynamic="true"]').forEach(link => link.remove());
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
				await initializeGame();
			} else if (url.includes('pong')) {
				await loadResource('/static/js/pong.js', 'script');
			} else if (url.includes('signup')) {
				attachPolicyListeners();
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
			{ id: 'navbar-games', url: '/games/' },
			{ id: 'edit-profile', url: '/edit_profile/' },
			{ id: 'edit-password', url: '/edit_password/' },
			{ id: 'games', url: '/games/' },
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
							if (id === 'logout-form' || id === 'delete-account-form') {
								loadContent('/home/', true);
								loadHeader();
							} else if (id === 'signup-form' || id === 'login-form' || id === 'edit-profile-form') {
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
		const privacyPolicyModal = new bootstrap.Modal(document.getElementById('privacyPolicyModal'));
		const acceptPrivacyPolicyBtn = document.getElementById('accept-privacy-policy');
		const privacyPolicyAgreement = document.getElementById('privacyPolicyAgreement');
		const signupSubmitBtn = document.getElementById('signup-submit');
		let privacyPolicyAccepted = localStorage.getItem('privacyPolicyAccepted') === 'true';

		if (!privacyPolicyAccepted) {
			privacyPolicyModal.show();
		} else {
			signupSubmitBtn.disabled = false;
		}

		if (acceptPrivacyPolicyBtn) {
			acceptPrivacyPolicyBtn.addEventListener('click', () => {
				if (privacyPolicyAgreement.checked) {
					localStorage.setItem('privacyPolicyAccepted', 'true');
					privacyPolicyModal.hide();
					signupSubmitBtn.disabled = false;
				} else {
					alert('You must agree to the privacy policy to proceed.');
				}
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