import EnemyController from "./EnemyController.js";
import Player from "./Player.js";
import BulletController from "./BulletController.js";
import Canvas from "./Canvas.js";
import { Color } from "./Colors.js";
import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { tournamentSetup } from "./Tournament.js";

let gameInstance;

export function startInvaders(userName) {

	gameInstance = new Canvas(userName);
	let mode;
	gameInstance.ctx.drawImage(gameInstance.gifCanvas, 0, 0, gameInstance.canvas.width, gameInstance.canvas.height);

	const menuScreen = createElement('div', { className: 'menu' },
		createElement('h1', { innerText: 'PUSHEEN\nINVADERS' }),
		createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
		createElement('div', { className: 'button-vertical' },
			createButton('ARCADE 1P', () => {
				menuScreen.remove();
				const player1 = new Player(gameInstance.canvas, 'Player1', 'player1');
				startGame(mode = 'arcade', player1, null);
			}),
			createButton('VERSUS 2P', () => {
				menuScreen.remove();
				const player1 = new Player(gameInstance.canvas, 'Player1', 'player1');
				const player2 = new Player(gameInstance.canvas, 'Player2', 'player2');
				player2.setAltControls();
				startGame(mode = 'versus', player1, player2);
			}),
			createButton('TOURNAMENT', () => {
				menuScreen.remove();
				tournamentSetup(startGame, gameInstance);
			})
		)
	);
	document.querySelector('.invaders-container').appendChild(menuScreen);

	// Start game with parameters
	function startGame(selectedMode, player1, player2, tournament) {
		let mode = selectedMode;
		gameInstance.isGameOver = false;
		gameInstance.didWin = false;


		const controlsScreen = createElement('div', { className: 'menu' });
		const controlsText = createElement('h2', { innerText: 'CONTROLS' });
		controlsScreen.appendChild(controlsText);

		const player1Info = displayControls(player1, controlsScreen, mode);
		let playerInfo;

		if (mode === 'arcade') {
			playerInfo = createElement('div', { className: 'button-horizontal' }, player1Info);
		} else if (mode === 'versus' || mode === 'tournament') {
			const player2Info = displayControls(player2, controlsScreen, mode);
			playerInfo = createElement('div', { className: 'button-horizontal' }, player1Info, player2Info);
		}

		controlsScreen.appendChild(playerInfo);

		const startButton = createButtonGreen('START GAME', () => {
			if (mode === 'versus' && player1.id === player2.id) {
					alertBox.style.color = 'red';
				setTimeout(() => { alertBox.style.color = 'transparent';}, 3000);
			} else {
				controlsScreen.remove();
				initializeMatch(mode, player1, player2);
			}
		});

		const backButton = createButton('MENU', () => {
			controlsScreen.remove();
			startInvaders(gameInstance.userName);
		});

		const buttonContainer = createElement('div', { className: 'button-horizontal' }, backButton, startButton);
		controlsScreen.appendChild(buttonContainer);

		const alertBox = createElement('div', { className: 'p',
			innerText: 'Players cannot have the same character!',
			style: 'color: transparent; font-size: 0.8em;' });
		controlsScreen.appendChild(alertBox);

		document.querySelector('.invaders-container').appendChild(controlsScreen);

		const enemyInfo = createElement('div', { className: 'button-horizontal', style: 'margin-top: 60px;' },
			createElement('div', { className: 'button-vertical', style: 'width: 150px;' },
				createElement('img', { src: '../../static/img/enemy1.png', width: 54, height: 54 }),
				createElement('p', { innerText: '10 PTS'})
			),
			createElement('div', { className: 'button-vertical', style: 'width: 150px;' },
				createElement('img', { src: '../../static/img/enemy2.png', width: 54, height: 54 }),
				createElement('p', { innerText: '20 PTS'})
			),
			createElement('div', { className: 'button-vertical', style: 'width: 150px;' },
				createElement('img', { src: '../../static/img/enemy3.png', width: 54, height: 54 }),
				createElement('p', { innerText: '30 PTS'})
			)
		);
		controlsScreen.appendChild(enemyInfo);

		// Display controls in the screen menu
		function displayControls(player, controlsScreen) {
			let playerImageContainer = createElement('div', { className: 'button-horizontal' });
			let playerTitle;
			if (mode !== 'tournament') {
				let index = 1;
				if (player.id === 'player2')
					index = 2;

				let playerImage = createElement('img', { src: `../../static/img/${player.id}.png`,
					width: 62, height: 70 });

				const leftButton = createArrowButton('<', () => {
					index = index === 1 ? 8 : index - 1;
					updatePlayerImage(index);
					updatePlayerTitleColor(Color[`player${index}`]);
					updatePlayerId(index);
				});
				const rightButton = createArrowButton('>', () => {
					index = index === 8 ? 1 : index + 1;
					updatePlayerImage(index);
					updatePlayerTitleColor(Color[`player${index}`]);
					updatePlayerId(index);
				});
				let name = mode === 'arcade' ? gameInstance.userName : player.name;
				appendChildren(playerImageContainer, leftButton, playerImage, rightButton);
				playerTitle = createElement('h3', { innerText: name, style: `color: ${player.color};` });

				function updatePlayerId(index) {player.updateId(index);}
				function updatePlayerTitleColor(color) { playerTitle.style.color = color;}
				function updatePlayerImage(index) { playerImage.src = `../../static/img/player${index}.png`;}
			}
			else {
				playerImageContainer = createElement('img', { src: `../../static/img/${player.id}.png`,
					width: 62, height: 70 });
				playerTitle = createElement('h3', { innerText: player.name, style: `color: ${player.color};` });
			}

			const moveImage = createElement('img', {
				src: `../../static/img/move${player.control}.png`,
				width: 124,
				height: 50,
				style: 'margin: 20px;'
			});
			controlsScreen.style.marginBottom = '30px';
			return createElement('div', { className: 'button-vertical' }, playerImageContainer, playerTitle, moveImage);
		}


		// Launche the function to initialize the game
		function initializeMatch(mode, player1, player2) {

			gameInstance.enemyBulletController = new BulletController(gameInstance.canvas, 4, "yellow", false);

			if (mode === 'arcade') {
				gameInstance.enemyController = new EnemyController(gameInstance.canvas, gameInstance.enemyBulletController, player1, null, mode);
			} else if (mode === 'versus' || mode === 'tournament') {
				player1.x = gameInstance.canvas.width / 4;
				player2.x = gameInstance.canvas.width / 4 * 3;
				player2.control = 2;
				gameInstance.enemyController = new EnemyController(gameInstance.canvas, gameInstance.enemyBulletController, player1, player2, mode);
			}
			gameInstance.gameInterval = setInterval(loopGame, 1000 / 60);
		}

		// Main game loop
		function loopGame() {
			checkGameOver();
			gameInstance.ctx.drawImage(gameInstance.gifCanvas, 0, 0, gameInstance.canvas.width, gameInstance.canvas.height);
			displayGameOver();
			if (!gameInstance.isGameOver) {
				gameInstance.enemyController.draw(gameInstance.ctx);
				player1.draw(gameInstance.ctx);
				player1.bulletController.draw(gameInstance.ctx);
				if (player2) {
					player2.draw(gameInstance.ctx);
					player2.bulletController.draw(gameInstance.ctx);
				}
				gameInstance.enemyBulletController.draw(gameInstance.ctx);
			} else if (mode === 'tournament') {
				tournament.onMatchEnd(player1, player2);
			}
		}

		// Display the game over screen
		function displayGameOver() {
			if (!gameInstance.isGameOver) return;
			clearInterval(gameInstance.gameInterval);

			if (mode === 'arcade' || mode === 'versus') {
				const gameOverScreen = createElement('div', { className: 'menu' });
				const titleText = createElement('h2', {});
				const scoreText = createElement('h4', {style: 'margin-bottom: 20px;'});
				let actionButton;
				let winner;

				if (mode === 'arcade') {
					saveScore(player1.score);
					titleText.innerText = "GAME OVER";
					titleText.style.color = "red";

					scoreText.innerText = `SCORE ${player1.score}`;

					actionButton = createElement('div', { className: 'button-horizontal' },
						createButton('MENU', () => {
							gameOverScreen.remove();
							resetGame(gameInstance);
							startInvaders(gameInstance.userName);
						}
					));
					appendChildren(gameOverScreen, titleText, scoreText, actionButton);

				} else if (mode === 'versus') {
					if (player1.score === player2.score) {
						titleText.innerText = "IT'S A TIE!";
						actionButton = createButton('TRY AGAIN', () => {
							gameOverScreen.remove();
							player1.reset();
							player2.reset();
							resetGame(gameInstance);
							startGame(mode, player1, player2);
						});
						appendChildren(gameOverScreen, titleText, actionButton);

					} else {
						winner = player1.score > player2.score ? player1 : player2;
						titleText.innerText = 'WINNER';
						const winnerName = createElement('h3', {
							innerText: winner.name,
							style: `color: ${winner.color};`
						});
						scoreText.innerText = `SCORE ${winner.score}`;

						if (mode === 'versus') {
							actionButton = createButton('BACK TO MENU', () => {
								gameOverScreen.remove();
								resetGame(gameInstance);
								startInvaders(gameInstance.userName);
							});
							appendChildren(gameOverScreen, titleText, winnerName, scoreText, actionButton);
						}
					}
				}
				document.querySelector('.invaders-container').appendChild(gameOverScreen);
			}
		}

		// Check if the game is over
		function checkGameOver() {
			if (gameInstance.isGameOver) return;

			if (gameInstance.enemyBulletController.collideWith(player1))
				player1.isDestroyed = true;
			if (gameInstance.enemyController.collideWith(player1) || gameInstance.enemyController.checkIfEnemiesReachedBottom()) {
				gameInstance.isGameOver = true;
			}

			if (mode === 'versus' || mode === 'tournament') {
				if (gameInstance.enemyBulletController.collideWith(player2))
					player2.isDestroyed = true;
				if (gameInstance.enemyController.collideWith(player2))
					gameInstance.isGameOver = true;
			}
			if (gameInstance.enemyController.enemyRows.length === 0) {
				gameInstance.isGameOver = true;
				gameInstance.didWin = true;
			}

			if (mode === 'arcade' && player1.isDestroyed)
				gameInstance.isGameOver = true;

			if ((mode === 'versus' || mode === 'tournament') && player1.isDestroyed
				&& player2.isDestroyed && gameInstance.isGameOver === false)
				gameInstance.isGameOver = true;
		}

		function saveScore(score) {
			fetch('/invaders/save_match/', {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
					'X-CSRFToken': getCookie('csrftoken')
				},
				body: JSON.stringify({ score: score }),
			})
			.then(response => response.json())
			.then(data => {
				if (data.status === 'success') {
					console.log('Score saved successfully in the database!');
				} else {
					console.error('Error saving score:', data.message);
				}
			})
			.catch(error => {
				console.error('Error: ', error);
			});
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
	}
}

// Start again from the main menu
export function resetGame(game) {
	game.isGameOver = false;
	game.didWin = false;
	clearInterval(game.gameInterval);
	game.enemyController = null;
	game.enemyBulletController = null;
}

export function stopInvaders() {
	if (gameInstance) {
		clearInterval(gameInstance.gameInterval);
		gameInstance = null;
	}
}
