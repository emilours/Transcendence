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
	// Cache DOM elements
	const appDiv = document.getElementById("app");
	const homeLink = document.getElementById("home");
	const loginLink = document.getElementById("login");
	const signupLink = document.getElementById("signup");

	// Attach event listeners to navigation links
	homeLink.addEventListener("click", (e) => {
		e.preventDefault();
		loadPage("home");
	});

	loginLink.addEventListener("click", (e) => {
		e.preventDefault();
		loadPage("login");
	});

	signupLink.addEventListener("click", (e) => {
		e.preventDefault();
		loadPage("signup");
	});

	// Handle history state changes (Back/Forward button)
	window.addEventListener("popstate", (event) => {
		if (event.state && event.state.page) {
			loadPage(event.state.page, false);
		} else {
			loadPage("home", false);
		}
	});

	// Load the initial page based on the URL
	const initialPage = window.location.pathname === "/login" ? "login" : (window.location.pathname === "/signup" ? "signup" : "home");
	loadPage(initialPage, false);

	// Function to load the content of a page
	function loadPage(page, pushState = true) {
		fetch(`/${page}/content/`)
			.then(response => response.text())
			.then(html => {
				appDiv.innerHTML = html;

				// Update URL and history state
				if (pushState) {
					const url = page === "home" ? "/" : `/${page}`;
					window.history.pushState({page: page}, null, url);
				}
			})
			.catch(error => {
				console.error('Error loading page:', error);
			});
	}
});
