import EnemyController from "./EnemyController.js";
import Player from "./Player.js";
import BulletController from "./BulletController.js";
import { Color } from "./Colors.js";
import { createElement, createButton, createPlayerContainer, backButton,
	shuffleArray, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import Tournament from "./Tournament.js";

// Config canvas
const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
canvas.width = 700;
canvas.height = 700;

// Gif background
const gifCanvas = document.createElement('canvas');
const gifAnimation = gifler('../../static/img/background.gif');
gifCanvas.width = canvas.width;
gifCanvas.height = canvas.height;
gifAnimation.get(function (a) {
	a.animateInCanvas(gifCanvas);
});

// Game variables
let		mode;
let		enemyController;
let		enemyBulletController;
let		isGameOver = false;
let		didWin = false;
let		gameInterval;
let		userName = 'USERNAME';

// Main menu
export function drawMenu() {
	ctx.drawImage(gifCanvas, 0, 0, canvas.width, canvas.height);

	const menuScreen = createElement('div', { className: 'menu', id: 'menuScreen' },
		createElement('h1', { innerText: 'PUSHEEN\nINVADERS' }),
		createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
		createElement('div', { className: 'button-vertical' },
			createButton('ARCADE 1P', () => {
				menuScreen.remove();
				const player1 = new Player(canvas, 'Player1', 'player1');
				startGame(mode = 'arcade', player1, null);
			}),
			createButton('VERSUS 2P', () => {
				menuScreen.remove();
				const player1 = new Player(canvas, 'Player1', 'player1');
				const player2 = new Player(canvas, 'Player2', 'player2');
				player2.setAltControls();
				startGame(mode = 'versus', player1, player2);
			}),
			createButton('TOURNAMENT', () => {
				menuScreen.remove();
				tournamentSetup();
			}),
			createButton('LEADERBOARD', () => {
				menuScreen.remove();
				displayLeaderboard();
			})
			// ,createButton('HISTORY', () => {
			// 	menuScreen.remove();
			// 	displayLeaderboard();
			// })
		)
	);
	document.body.appendChild(menuScreen);
}

// Create the setup tournament screen
function tournamentSetup() {
	const playerList = new Array();
	const playerListContainer = createElement('div', { className: 'player-list' });

	const tournamentScreen = createElement('div', { className: 'menu' },
		createElement('h2', { innerText: 'Tournament' }),
		createElement('h3', { innerText: 'SELECT A SIZE' }),
		createButton('4 PLAYER', () => setupPlayers(4)),
		createButton('8 PLAYERS', () => setupPlayers(8)),
		playerListContainer,
		createElement('div', { className: 'button-horizontal' },
			createButton('MENU', () => {
				backButton(tournamentScreen, drawMenu);
			}),
			createButtonGreen('CREATE', () => {
				if (playerList.length === 4 || playerList.length === 8) {
					tournamentScreen.style.display = 'none';
					shuffleArray(playerList);
					createTournament(new Tournament(canvas, playerList));
				} else {
					alertBox.style.color = 'red';
					setTimeout(() => {
						alertBox.style.color = 'transparent';}, 3000);
				}
			})
		)
	);
	const alertBox = createElement('div', { className: 'p',
		innerText: 'Select a size before continue!',
		style: 'color: transparent; font-size: 0.8em;' });
	tournamentScreen.appendChild(alertBox);
	document.body.appendChild(tournamentScreen);

	function setupPlayers(num) {
		playerListContainer.innerHTML = '';
		playerList.length = 0;

		for (let i = 1; i <= num; i++) {
			const color = Color[`player${i}`];
			const playerContainer = createPlayerContainer(i, color, playerList);
			playerListContainer.appendChild(playerContainer);
		}
	}

	function createTournament(tournament) {
		tournament.playNextMatch();
	}
}

// Start game with parameters
export function startGame(selectedMode, player1, player2, tournament) {
	mode = selectedMode;
	isGameOver = false;
	didWin = false;


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
			initializeGame(mode, player1, player2);
		}
	});

	const backButton = createButton('MENU', () => {
		controlsScreen.remove();
		drawMenu();
	});

	const buttonContainer = createElement('div', { className: 'button-horizontal' }, backButton, startButton);
	controlsScreen.appendChild(buttonContainer);

	const alertBox = createElement('div', { className: 'p',
		innerText: 'Players cannot have the same character!',
		style: 'color: transparent; font-size: 0.8em;' });
	controlsScreen.appendChild(alertBox);

	document.body.appendChild(controlsScreen);

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
			let name = mode === 'arcade' ? userName : player.name;
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
	function initializeGame(mode, player1, player2) {

		enemyBulletController = new BulletController(canvas, 4, "yellow", false);

		if (mode === 'arcade') {
			enemyController = new EnemyController(canvas, enemyBulletController, player1, null, mode);
		} else if (mode === 'versus' || mode === 'tournament') {
			player1.x = canvas.width / 4;
			player2.x = canvas.width / 4 * 3;
			player2.control = 2;
			enemyController = new EnemyController(canvas, enemyBulletController, player1, player2, mode);
		}
		gameInterval = setInterval(game, 1000 / 60);
	}

	// Main game loop
	function game() {
		checkGameOver();
		ctx.drawImage(gifCanvas, 0, 0, canvas.width, canvas.height);
		displayGameOver();
		if (!isGameOver) {
			enemyController.draw(ctx);
			player1.draw(ctx);
			player1.bulletController.draw(ctx);
			if (player2) {
				player2.draw(ctx);
				player2.bulletController.draw(ctx);
			}
			enemyBulletController.draw(ctx);
		} else if (mode === 'tournament')
			tournament.onMatchEnd(player1, player2);
	}

	// Display the game over screen
	function displayGameOver() {
		if (!isGameOver) return;
		clearInterval(gameInterval);

		if (mode === 'arcade' || mode === 'versus') {
			const gameOverScreen = createElement('div', { className: 'menu' });
			const titleText = createElement('h2', {});
			const scoreText = createElement('h4', {style: 'margin-bottom: 20px;'});
			let actionButton;
			let winner;

			if (mode === 'arcade') {
				titleText.innerText = "GAME OVER";
				titleText.style.color = "red";

				scoreText.innerText = `SCORE ${player1.score}`;

				actionButton = createElement('div', { className: 'button-horizontal' },
					createButton('MENU', () => {
						gameOverScreen.remove();
						resetGame();
						drawMenu();
					}),
					createButtonGreen('SAVE SCORE', () => {
						gameOverScreen.remove();
						saveScore(player1.score);
						resetGame();
						drawMenu();
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
						resetGame();
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
							resetGame();
							drawMenu();
						});
						appendChildren(gameOverScreen, titleText, winnerName, scoreText, actionButton);
					}
				}
			}
			document.body.appendChild(gameOverScreen);
		}
	}

	// Check if the game is over
	function checkGameOver() {
		if (isGameOver) return;

		if (enemyBulletController.collideWith(player1))
			player1.isDestroyed = true;
		if (enemyController.collideWith(player1) || enemyController.checkIfEnemiesReachedBottom()) {
			isGameOver = true;
		}

		if (mode === 'versus' || mode === 'tournament') {
			if (enemyBulletController.collideWith(player2))
				player2.isDestroyed = true;
			if (enemyController.collideWith(player2))
				isGameOver = true;
		}
		if (enemyController.enemyRows.length === 0) {
			isGameOver = true;
			didWin = true;
		}

		if (mode === 'arcade' && player1.isDestroyed)
			isGameOver = true;

		if ((mode === 'versus' || mode === 'tournament') && player1.isDestroyed
			&& player2.isDestroyed && isGameOver === false)
			isGameOver = true;
	}

	function saveScore(score) {
		const leaderboardKey = 'leaderboard';
		const leaderboard = JSON.parse(localStorage.getItem(leaderboardKey)) || [];

		leaderboard.push({ userName, score });
		localStorage.setItem(leaderboardKey, JSON.stringify(leaderboard));

		console.log('Score saved successfully!');
	}
}

function displayLeaderboard() {
	const leaderboard = JSON.parse(localStorage.getItem('leaderboard')) || [];
	leaderboard.sort((a, b) => b.score - a.score);

	const leaderboardScreen = createElement('div', { className: 'menu'});
	const title = createElement('h2', { innerText: 'LEADERBOARD' });
	leaderboardScreen.appendChild(title);

	const list = createElement('div', { className: 'list-leader' });
	const itemList = createElement('div', { className: 'list' },
		createElement('p', { innerText: 'RANK', style: 'width: 60px;' }),
		createElement('p', { innerText: 'USER', style: 'width: 200px;' }),
		createElement('p', { innerText: 'SCORE' , style: 'width: 100px;'})
	);
	list.appendChild(itemList);

	let i = 0;
	leaderboard.slice(0, 10).forEach(entry => {
		const itemList = createElement('div', { className: 'list' },
			createElement('h4', { innerText: `${++i}.`, style: 'width: 60px;'  }),
			createElement('h4', { innerText: entry.userName, style: 'width: 200px;' }),
			createElement('h4', { innerText: entry.score, style: 'width: 100px;' })
		);
		itemList.style.display = 'flex';
		itemList.style.alignItems = 'center';
		list.appendChild(itemList);
	});
	leaderboardScreen.appendChild(list);

	const backButton = createButton('MENU', () => {
		leaderboardScreen.remove();
		drawMenu();
	});
	leaderboardScreen.appendChild(backButton);
	document.body.appendChild(leaderboardScreen);
}

// Start again from the main menu
export function resetGame() {
	isGameOver = false;
	didWin = false;
	clearInterval(gameInterval);
	enemyController = null;
	enemyBulletController = null;
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}

drawMenu();
