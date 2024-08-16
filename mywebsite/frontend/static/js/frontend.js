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

	function loadContent(url) {
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
			attachListeners();
		})
		.catch(error => console.error('Error:', error));
	}

	document.getElementById('home').addEventListener('click', function (event) {
		event.preventDefault();
		loadContent('/home/');
	});

	document.getElementById('navbar-login').addEventListener('click', function (event) {
		event.preventDefault();
		loadContent('/login/');
	});

	document.getElementById('navbar-signup').addEventListener('click', function (event) {
		event.preventDefault();
		loadContent('/signup/');
	});

	function attachListeners() {
		// const homeLink = document.getElementById('home');
		const loginLink = document.getElementById('login');
		const signupLink = document.getElementById('signup');

		// if (homeLink) {
		// 	homeLink.addEventListener('click', function (event) {
		// 		event.preventDefault();
		// 		loadContent('/home/');
		// 	});
		// }

		if (loginLink) {
			loginLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/login/');
			});
		}

		if (signupLink) {
			signupLink.addEventListener('click', function (event) {
				event.preventDefault();
				loadContent('/signup/');
			});
		}
	}

	window.addEventListener('popstate', (event) => {
		if (event.state && event.state.route) {
			handleRoute(event.state.route, false);
		} else {
			handleRoute('home', false);
		}
	});
	// Initial load
	loadContent('/home/');
});
