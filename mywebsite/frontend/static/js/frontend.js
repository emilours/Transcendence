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

	const app = document.getElementById('app');

	function loadScript(url) {
		return new Promise((resolve, reject) => {
			const script = document.createElement('script');
			script.src = url;
			script.type = "module";
			script.onload = resolve;
			script.onerror = reject;
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
			document.head.appendChild(link);
		});
	}

	function loadContent(url, addToHistory = true) {
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
				// Charger dynamiquement gifler avant invaders.js
				loadScript('https://cdn.jsdelivr.net/npm/gifler@0.1.0/gifler.min.js')
				.then(() => loadCSS('/static/css/invaders.css'))
				.then(() => loadScript('/static/js/invaders.js'))
				.catch(error => console.error('Error loading scripts:', error));
			}

			// if (url.includes('invaders')) {
			// 	loadScript('/static/js/invaders.js');
			// 	loadCSS('/static/css/invaders.css');
			// }

			attachListeners();

			if (addToHistory) {
				history.pushState({ route: url }, null, url);
			}
		})
		.catch(error => console.error('Error:', error));
	}


	// document.getElementById('home').addEventListener('click', function (event) {
	// 	event.preventDefault();
	// 	loadContent('/home/');
	// });

	document.getElementById('navbar-login').addEventListener('click', function (event) {
		event.preventDefault();
		loadContent('/signin/', true);
	});

	document.getElementById('navbar-signup').addEventListener('click', function (event) {
		event.preventDefault();
		loadContent('/signup/', true);
	});


	function attachListeners() {
		const homeLink = document.getElementById('home');
		const loginLink = document.getElementById('login');
		const signupLink = document.getElementById('signup');
		// const loginLinks = document.querySelectorAll('login', 'navbar-login');
		// const signupLinks = document.querySelectorAll('signup', 'navbar-signup');
		const gameLink = document.getElementById('games');
		const invadersLink = document.getElementById('invaders');

		if (homeLink) {
			homeLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/home/', true);
			});
		}

		if (loginLink) {
			loginLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/sigin/', true);
			});
		}

		if (signupLink) {
			signupLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/signup/', true);
			});
		}
		// if (loginLinks.length > 0) {
		// 	loginLinks.forEach(link => {
		// 		link.addEventListener('click', function (event) {
		// 			event.preventDefault();
		// 			loadContent('/login/', true);
		// 		});
		// 	});
		// }

		// if (signupLinks.length > 0) {
		// 	signupLinks.forEach(link => {
		// 		link.addEventListener('click', function (event) {
		// 			event.preventDefault();
		// 			loadContent('/signup/', true);
		// 		});
		// 	});
		// }

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
	}

	window.addEventListener('popstate', (event) => {
		if (event.state && event.state.route) {
			loadContent(event.state.route, false);
		} else {
			loadContent('/home/', false);
		}
	});


	// Initial load
	loadContent('/home/');


});
