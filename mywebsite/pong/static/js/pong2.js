import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
// import { ConnectWebsocket, StartGame } from './pong.js';

export function initPong(userName) {
	console.log('Pong game initialized - user:', userName);

	const menuScreen = createElement('div', { className: 'menu' },
		createElement('h1', { innerText: 'PUSHEEN\nPONG' }),
		createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
		createElement('div', { className: 'button-vertical' },
			createButton('ONLINE MATCH', () => {
				menuScreen.remove();
				// const player1 = new Player(game.canvas, 'Player1', 'player1');
				// startGame(mode = 'online', player1, null);
			}),
			createButton('LOCAL MATCH', () => {
				menuScreen.remove();
				// const player1 = new Player(game.canvas, 'Player1', 'player1');
				// const player2 = new Player(game.canvas, 'Player2', 'player2');
				// StartGame();
			}),
			createButton('TOURNAMENT', () => {
				menuScreen.remove();
				// tournamentSetup(startGame, game);
			})
		)
	);
	document.querySelector('.pong-container').appendChild(menuScreen);

	// Start game with parameters

		// function saveScore(score) {
		// 	fetch('/invaders/save_match/', {
		// 		method: 'POST',
		// 		headers: {
		// 			'Content-Type': 'application/json',
		// 			'X-CSRFToken': getCookie('csrftoken')
		// 		},
		// 		body: JSON.stringify({ score: score }),
		// 	})
		// 	.then(response => response.json())
		// 	.then(data => {
		// 		if (data.status === 'success') {
		// 			console.log('Score saved successfully in the database!');
		// 		} else {
		// 			console.error('Error saving score:', data.message);
		// 		}
		// 	})
		// 	.catch(error => {
		// 		console.error('Error: ', error);
		// 	});
		// }

		// function getCookie(name) {
		// 	let cookieValue = null;
		// 	if (document.cookie && document.cookie !== '') {
		// 		const cookies = document.cookie.split(';');
		// 		for (let i = 0; i < cookies.length; i++) {
		// 			const cookie = cookies[i].trim();
		// 			if (cookie.substring(0, name.length + 1) === (name + '=')) {
		// 				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
		// 				break;
		// 			}
		// 		}
		// 	}
		// 	return cookieValue;
		// }

}

// initPong();
