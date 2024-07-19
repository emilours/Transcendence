document.addEventListener('DOMContentLoaded', function() {
	const app = document.getElementById('app');

	function renderHome() {
		app.innerHTML = `
			<section class="py-5" id="johndoe">
				<div class="container">
					<div class="row align-items-center gy-4">
						<div class="col-12 col-md-6">
							<h1 class="fw-bold">Je suis <b class="fw-bold">Pusheen Arcade</h1>
						</div>
						<div class="col-12 col-md-6">
							<img src="./img/pusheen_drink.png" alt="john doe" description="hello" width="100%">
						</div>
					</div>
				</div>
			</section>
		`;
	}

	function renderAbout() {
		app.innerHTML = `
			<h1>À propos</h1>
			<p>Ceci est la page à propos.</p>
		`;
	}

	function renderContact() {
		app.innerHTML = `
			<h1>Contact</h1>
			<p>Ceci est la page de contact.</p>
		`;
	}

	function handleRoute(route, addToHistory = true) {
		switch(route) {
			case 'home':
				renderHome();
				break;
			case 'about':
				renderAbout();
				break;
			case 'contact':
				renderContact();
				break;
			default:
				renderHome();
		}

		if (addToHistory) {
			history.pushState({ route }, '', `#${route}`);
		}
	}

	document.getElementById('home').addEventListener('click', (event) => {
		event.preventDefault();
		handleRoute('home');
	});

	document.getElementById('about').addEventListener('click', (event) => {
		event.preventDefault();
		handleRoute('about');
	});

	document.getElementById('contact').addEventListener('click', (event) => {
		event.preventDefault();
		handleRoute('contact');
	});


	window.addEventListener('popstate', (event) => {
		if (event.state && event.state.route) {
			handleRoute(event.state.route, false);
		} else {
			handleRoute('home', false);
		}
	});

	// Charger la page actuelle basée sur le hash ou la page d'accueil par défaut
	const initialRoute = window.location.hash.replace('#', '') || 'home';
	handleRoute(initialRoute, false);
});

// document.addEventListener('DOMContentLoaded', function() {
// 	const app = document.getElementById('app');
// 	const navContainer = document.getElementById('nav-container');

// 	let isAuthenticated = false; // Changez cette variable pour simuler l'état de connexion

// 	function renderNav() {
// 		if (isAuthenticated) {
// 			navContainer.innerHTML = `
// 				<nav>
// 					<a href="/" id="home">Accueil</a>
// 					<a href="/about" id="about">À propos</a>
// 					<a href="/contact" id="contact">Contact</a>
// 					<a href="/logout" id="logout">Déconnexion</a>
// 				</nav>
// 			`;
// 			document.getElementById('logout').addEventListener('click', (event) => {
// 				event.preventDefault();
// 				logout();
// 			});
// 		} else {
// 			navContainer.innerHTML = `
// 				<nav>
// 					<a href="/" id="home">Accueil</a>
// 					<a href="/about" id="about">À propos</a>
// 					<a href="/contact" id="contact">Contact</a>
// 					<a href="/login" id="login">Connexion</a>
// 				</nav>
// 			`;
// 			document.getElementById('login').addEventListener('click', (event) => {
// 				event.preventDefault();
// 				login();
// 			});
// 		}

// 		document.getElementById('home').addEventListener('click', (event) => {
// 			event.preventDefault();
// 			handleRoute('/');
// 		});
// 		document.getElementById('about').addEventListener('click', (event) => {
// 			event.preventDefault();
// 			handleRoute('/about');
// 		});
// 		document.getElementById('contact').addEventListener('click', (event) => {
// 			event.preventDefault();
// 			handleRoute('/contact');
// 		});
// 	}

// 	function renderHome() {
// 		app.innerHTML = `
// 			<h1>Bienvenue</h1>
// 			<p>Ceci est la page d'accueil.</p>
// 		`;
// 	}

// 	function renderAbout() {
// 		app.innerHTML = `
// 			<h1>À propos</h1>
// 			<p>Ceci est la page à propos.</p>
// 		`;
// 	}

// 	function renderContact() {
// 		app.innerHTML = `
// 			<h1>Contact</h1>
// 			<p>Ceci est la page de contact.</p>
// 		`;
// 	}

// 	function handleRoute(route, addToHistory = true) {
// 		switch(route) {
// 			case '/':
// 				renderHome();
// 				break;
// 			case '/about':
// 				renderAbout();
// 				break;
// 			case '/contact':
// 				renderContact();
// 				break;
// 			default:
// 				renderHome();
// 		}

// 		if (addToHistory) {
// 			history.pushState({ route }, '', route);
// 		}
// 	}

// 	function login() {
// 		isAuthenticated = true;
// 		renderNav();
// 		handleRoute('/');
// 	}

// 	function logout() {
// 		isAuthenticated = false;
// 		renderNav();
// 		handleRoute('/');
// 	}

// 	window.addEventListener('popstate', (event) => {
// 		if (event.state && event.state.route) {
// 			handleRoute(event.state.route, false);
// 		} else {
// 			handleRoute('/', false);
// 		}
// 	});

// 	// Charger la page actuelle basée sur l'URL ou la page d'accueil par défaut
// 	const initialRoute = window.location.pathname || '/';
// 	renderNav();
// 	handleRoute(initialRoute, false);
// });
