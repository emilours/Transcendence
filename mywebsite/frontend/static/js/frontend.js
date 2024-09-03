import { initializeGame } from '/static/js/invaders.js';

document.addEventListener("DOMContentLoaded", () => {
	// Fontsize + or -
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

	function showAlert(message) {
		const alertContainer = document.getElementById('alert-container');
		const alertMessage = document.getElementById('alert-message');

		alertMessage.textContent = message;
		alertContainer.classList.remove('d-none');

		// Masquer l'alerte après 5 secondes
		setTimeout(() => {
			alertContainer.classList.add('d-none');
		}, 500000);
	}

	function closeAlert() {
		document.getElementById('alert-container').classList.add('d-none');
	}



	const app = document.getElementById('app');

	function loadScript(url) {
		return new Promise((resolve, reject) => {
			const script = document.createElement('script');
			script.src = url;
			script.type = "module";
			script.onload = resolve;
			script.onerror = reject;
			script.dataset.dynamic = true;
			document.head.appendChild(script);
		});
	}

	function loadCSS(url) {
		return new Promise((resolve, reject) => {
			const link = document.createElement('link');
			link.rel = 'stylesheet';
			link.href = url;
			link.onload = resolve;
			link.onerror = reject;
			link.dataset.dynamic = true;
			document.head.appendChild(link);
		});
	}

	function cleanupResources() {
		// Supprimer les scripts et CSS ajoutés dynamiquement
		document.querySelectorAll('script[data-dynamic="true"]').forEach(script => script.remove());
		document.querySelectorAll('link[data-dynamic="true"]').forEach(link => link.remove());

		// Nettoyer les résidus de l'animation ou du contenu
		// if (typeof cleanupInvaders === 'function') {
		// 	cleanupInvaders();  // Assurez-vous que invaders.js contient une fonction de nettoyage
		// }
	}

	function loadContent(url, addToHistory = true) {
		cleanupResources();
		fetch(url, {
			headers: {
				'X-Requested-With': 'XMLHttpRequest'
			}
		})
		.then(response => {
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			return response.json();
		})
		.then(data => {
			app.innerHTML = data.html;

			if (url.includes('invaders')) {
				loadScript('https://cdn.jsdelivr.net/npm/gifler@0.1.0/gifler.min.js')
				.then(() => loadCSS('/static/css/invaders.css'))
				.then(() => loadScript('/static/js/invaders.js'))
				.then(() => initializeGame())
				.catch(error => console.error('Error loading scripts:', error));
			}

			if (url.includes('pong')) {
				loadScript('/static/js/pong.js')
				// .then(() => loadScript('/static/js/pong.js'))
				.catch(error => console.error('Error loading scripts:', error));
			}

			attachListeners();

			if (addToHistory) {
				history.pushState({ route: url }, null, url);
			}
		})
		.catch(error => console.error('Error:', error));
	}

	function attachListeners() {
		const homeLink = document.getElementById('home');
		const loginLink = document.getElementById('login');
		const signupLink = document.getElementById('signup');
		const signupNavLink = document.getElementById('navbar-signup');
		const loginNavLink = document.getElementById('navbar-login');
		const profileNavLink = document.getElementById('navbar-profile');
		const leaderNavLink = document.getElementById('navbar-leaderboard');
		const gameLink = document.getElementById('games');
		const invadersLink = document.getElementById('invaders');
		const pongLink = document.getElementById('pong');

		const signupForm = document.getElementById('signup-form');
		const loginForm = document.getElementById('login-form');
		const logoutForm = document.getElementById('logout-form');
		const addFriendForm = document.getElementById('add-friend-form');

		if (homeLink) {
			homeLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/home/', true);
			});
		}

		if (loginLink) {
			loginLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/login/', true);
			});
		}

		if (signupLink) {
			signupLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/signup/', true);
			});
		}

		if (signupNavLink) {
			signupNavLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/signup/', true);
			});
		}

		if (loginNavLink) {
			loginNavLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/login/', true);
			});
		}

		if (profileNavLink) {
			profileNavLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/profile/', true);
			});
		}

		if (leaderNavLink) {
			leaderNavLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/leaderboard/', true);
			});
		}

		if (gameLink) {
			gameLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/games/', true);
			});
		}

		if (invadersLink) {
			invadersLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/invaders/', true);
			});
		}

		if (pongLink) {
			pongLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/pong/', true);
			});
		}

		if (signupForm) {
			signupForm.addEventListener('submit', function(event) {
				event.preventDefault();

				const formData = new FormData(signupForm);

				fetch('/auth/signup/', {
					method: 'POST',
					body: formData,
					headers: {
						'X-Requested-With': 'XMLHttpRequest',
						"X-CSRFToken": csrftoken
					},
				})
				.then(response => response.json())
				.then(data => {
					if (data.error) {
						alert(data.error);
					} else {
						window.location.href = '/profile/';
					}
				})
				.catch(error => console.error('Error:', error));
			});
		}

		if (loginForm) {
			loginForm.addEventListener('submit', function(event) {
				event.preventDefault();

				const formData = new FormData(loginForm);

				fetch('/auth/signin/', {
					method: 'POST',
					body: formData,
					headers: {
						'X-Requested-With': 'XMLHttpRequest',
						"X-CSRFToken": csrftoken
					},
				})
				.then(response => response.json())
				.then(data => {
					if (data.error) {
						alert(data.error);  // Gérer les erreurs de validation ici
					} else {
						window.location.href = '/profile/';
					}
				})
				.catch(error => console.error('Error:', error));
			});
		}

		if (logoutForm)	{
			logoutForm.addEventListener('submit', function(event) {
				event.preventDefault();

				fetch('/auth/signout/', {
					method: 'POST',
					headers: {
						'X-Requested-With': 'XMLHttpRequest',
						"X-CSRFToken": csrftoken
					},
				})
				.then(response => response.json())
				.then(data => {
					if (data.error) {
						alert(data.error);  // Gérer les erreurs de validation ici
					} else {
						window.location.href = '/home/';
					}
				})
				.catch(error => console.error('Error:', error));
			});
		}

		if (addFriendForm) {
			addFriendForm.addEventListener('submit', function(event) {
				event.preventDefault();

				const formData = new FormData(addFriendForm);

				fetch('/auth/send_friend_request/', {
					method: 'POST',
					body: formData,
					headers: {
						'X-Requested-With': 'XMLHttpRequest',
						'X-CSRFToken': csrftoken
					},
				})
				.then(response => response.json())
				.then(data => {
					if (data.error) {
						showAlert(data.error);
					} else {
						window.location.href = '/profile/';
					}
				})
				.catch(error => console.error('Error:', error));
			});
		}
	}

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
	const csrftoken = getCookie('csrftoken');

	window.addEventListener('popstate', (event) => {
		const currentPath = window.location.pathname;
		loadContent(currentPath, false);
	});

	function loadInitialContent() {
		const currentPath = window.location.pathname;
		loadContent(currentPath, false);
	}

	loadInitialContent();
});
