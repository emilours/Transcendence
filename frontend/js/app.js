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
	function renderHome() {
		app.innerHTML = `
		<section class="py-md-5 mt-5">
			<div class="container">
				<div class="row g-4">
					<div class="col-12 col-md-6 d-flex justify-content-center">
						<img src="./img/pusheen_drink.png" alt="john doe" description="hello" width="75%">
					</div>
					<div class="col-12 col-md-6 mt-4 d-flex align-items-center justify-content-center">
						<video controls class="w-100 rounded-3 border border-5 border-primary">
							<source src="./video/pusheen_the_cat_intro.mp4" type="video/mp4"/>
							<p>
								Votre navigateur ne prend pas en charge les vidéos HTML5. Voici
								<a href="myVideo.mp4">un lien pour télécharger la vidéo</a>.
							</p>
						</video>
					</div>
				</div>
			</div>
		</section>

		<section class="py-md-5 mt-4">
			<div class="container">
				<p>Pong is a table tennis–themed twitch arcade sports video game, featuring simple two-dimensional graphics, manufactured by Atari and originally released
					on 29 November 1972. It was one of the earliest arcade video games; it was created by Allan Alcorn as a training exercise assigned to him
					by Atari co-founder Nolan Bushnell, but Bushnell and Atari co-founder Ted Dabney were surprised by the quality of Alcorn's work and decided to manufacture the game.</p>
				<p>Pong was the first commercially successful video game, and it helped to establish the video game industry along with the Magnavox Odyssey.
					Soon after its release, several companies began producing games that closely mimicked its gameplay.</p>
			</div>
		</section>

		<section class="py-md-5 mt-2 font-potta">
			<div class="container">
				<div class="row g-4 justify-content-evenly mx-2">
					<div class="col-12 col-md-4 bg-primary d-flex flex-column align-items-center justify-content-center rounded-3 p-4">
						<h1 class="fw-bold text-center">Pusheen Arcade</h1>
						<button type="button" class="btn btn-info mt-3 rounded-3 bg-secondary">Play Now</button>
					</div>
					<div class="col-12 col-md-4">
						<img src="./img/pusheen.gif" alt="pusheen drinking" description="hello" class="rounded-3 w-100 border border-5 border-secondary">
					</div>
				</div>
			</div>
		</section>
		`;
	}

	function renderSignUp() {
		app.innerHTML = `
		<section class="vh-100 d-flex align-items-center justify-content-center">
			<div class="container">
				<div class="row justify-content-center">
					<div class="col-12 col-md-8 col-lg-6">
						<div class="card shadow">
							<div class="card-body p-5">
								<h3 class="card-title text-center mb-4 font-potta">Sign Up</h3>
								<form method='POST'>
									<div class="mb-3">
										<label for="firstName" class="form-label">First Name</label>
										<input type="text" class="form-control" id="firstName" required>
									</div>
									<div class="mb-3">
										<label for="lastName" class="form-label">Last Name</label>
										<input type="text" class="form-control" id="lastName" required>
									</div>
									<div class="mb-3">
										<label for="email" class="form-label">Email Address</label>
										<input type="email" class="form-control" id="email" required>
									</div>
									<div class="mb-3">
										<label for="password" class="form-label">Password</label>
										<input type="password" class="form-control" id="password" required>
									</div>
									<div class="mb-3">
										<label for="confirmPassword" class="form-label">Confirm Password</label>
										<input type="password" class="form-control" id="confirmPassword" required>
									</div>
									<button type="submit" class="btn btn-primary w-100">Sign Up</button>
								</form>
							</div>
						</div>
						<div class="text-center mt-3">
							<a href="#" class="text-decoration-none" id="login">Already have an account? Login</a>
						</div>
					</div>
				</div>
			</div>
		</section>
		`;
	}

	function renderLogin() {
		app.innerHTML = `
		<section class="vh-100 d-flex align-items-center justify-content-center">
			<div class="container my-5">
				<div class="row justify-content-center">
					<div class="col-12 col-md-6 col-lg-4">
						<div class="card shadow">
							<div class="card-body p-5">
								<h3 class="card-title text-center mb-4 font-potta">Login</h3>
								<form class="font-roboto" method='POST'>
									<div class="mb-3">
										<label for="email" class="form-label"></label>
										<input type="email" class="form-control" id="email" placeholder="Email" aria-describedby="emailHelp" required>
									</div>
									<div class="mb-3">
										<label for="password" class="form-label"></label>
										<input type="password" class="form-control" id="password" placeholder="Password" required>
									</div>
									<div class="my-4 form-check">
										<input type="checkbox" class="form-check-input" id="rememberMe">
										<label class="form-check-label" for="rememberMe">Remember me</label>
									</div>
									<button type="submit" class="btn btn-primary w-100">Login</button>
									<div class="text-center mt-3">
										<a href="#" class="text-decoration-none">Forgot password?</a>
									</div>
								</form>
							</div>
						</div>
						<div class="text-center mt-3 font-roboto">
							<p>Don't have an account? <a href="#signup" class="text-decoration-none" id="signup">Sign up</a></p>
						</div>
					</div>
				</div>
			</div>
		</section>
		`;
	}

	function handleRoute(route, addToHistory = true) {
		switch(route) {
			case 'home':
				renderHome();
				break;
			case 'signup':
				renderSignUp();
				break;
			case 'login':
				renderLogin();
				break;
			default:
				renderHome();
		}

		if (addToHistory) {
			history.pushState({ route }, '', `#${route}`);
		}
	}


	document.addEventListener('click', (event) => {
		if (event.target.matches('#home')) {
			event.preventDefault();
			handleRoute('home');
		} else if (event.target.matches('#signup')) {
			event.preventDefault();
			handleRoute('signup');
		} else if (event.target.matches('#login')) {
			event.preventDefault();
			handleRoute('login');
		}
	});

	// document.getElementById('home').addEventListener('click', (event) => {
	// 	event.preventDefault();
	// 	handleRoute('home');
	// });

	// document.getElementById('signup').addEventListener('click', (event) => {
	// 	event.preventDefault();
	// 	handleRoute('signup');
	// });

	// document.getElementById('login').addEventListener('click', (event) => {
	// 	event.preventDefault();
	// 	handleRoute('login');
	// });

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

