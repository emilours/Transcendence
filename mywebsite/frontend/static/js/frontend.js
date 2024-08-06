document.addEventListener('DOMContentLoaded', function() {
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

	// SPA
	const app = document.getElementById('app');

	function renderPage(url) {
		fetch(url)
			.then(response => response.text())
			.then(html => {
				app.innerHTML = html;
				window.history.pushState(null, '', url);
			})
			.catch(error => console.warn('Error loading page:', error));
	}

	document.getElementById('login').addEventListener('click', function() {
		renderPage('/login/');
	});

	document.getElementById('signup').addEventListener('click', function() {
		renderPage('/signup/');
	});

	window.addEventListener('popstate', function() {
		renderPage(window.location.pathname);
	});

	renderPage(window.location.pathname);
});
