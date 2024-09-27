import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket, CloseWebsocket, SendEvent, GetUsers } from './pong.js';

export function initPong(userName) {
	// let user = 'userName';
	var lobbyMenu;
	console.log('Pong game initialized - user:', userName);

	function drawMainMenu() {
		const mainMenu = createElement('div', { className: 'menu' },
			createElement('h1', { innerText: 'PUSHEEN\nPONG' }),
			createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
			createElement('div', { className: 'button-vertical' },
				createButton('ONLINE MATCH', () => {
					mainMenu.remove();
					drawOnlineMenu();
				}),
				createButton('LOCAL MATCH', () => {
					mainMenu.remove();
					drawLobbyLocal();
				}),
				createButton('TOURNAMENT', () => {
					mainMenu.remove();
					drawTournament();
				})
			)
		);
		document.querySelector('.pong-container').appendChild(mainMenu);
	}

	function drawOnlineMenu() {
		const onlineMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'ONLINE MATCH' }),
			createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
			createElement('div', { className: 'button-vertical' },
				createButton('CREATE LOBBY', () => {
					onlineMenu.remove();
					// FOR DEVELOPMENT
					console.log("CREATE LOBBY button clicked")
					// CloseWebsocket();
					ConnectWebsocket('normal', userName);
					//
					drawLobbyOnline('create');
				}),
				createButton('JOIN LOBBY', () => {
					onlineMenu.remove();
					// Need to change so it only joins
					// CloseWebsocket();
					ConnectWebsocket('normal', userName);
					drawLobbyOnline('join');
				}),
				createButton('BACK', () => {
					onlineMenu.remove();
					drawMainMenu();
				})
			)
		);
		document.querySelector('.pong-container').appendChild(onlineMenu);
	}

	function drawLobbyOnline(mode) {
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'ONLINE MATCH' }),
			createElement('h3', { innerText: 'LOBBY', style: 'margin-bottom: 20px;' }),
		);

		let player1Info;
		let player2Info;

		if (mode === 'create') {
			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerOnline(userName),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerOnline('waiting'),
			);
			lobbyMenu.appendChild(playerInfo);
		}
		else {
			var [user1, user2 ] = GetUsers();
			console.log('userName: ' + userName + ' | user1: ' + user1 + ' | user2: ' + user2);

			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerOnline(user1),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerOnline(userName),
			);
			lobbyMenu.appendChild(playerInfo);
		}

		const backButton = createButton('BACK', () => {
			document.querySelector('.menu').remove();
			drawOnlineMenu();
		});
		lobbyMenu.appendChild(backButton);

		document.querySelector('.pong-container').appendChild(lobbyMenu);
	}

	function drawPlayerOnline(userName) {
		if (userName === 'waiting') {
			const playerInfo = createElement('div', { className: 'button-vertical' },
				createElement('img', { src: '/static/img/loading.gif', width: 70, height: 70, style: 'margin: 65px;' }),
				createElement('h4', { innerText: 'Waiting for a player' })
			);
			return playerInfo;
		}

		let buttonReady;

		const playerInfo = createElement('div', { className: 'button-vertical' },
			createElement('img', { src: '/static/img/avatarDefault.gif', width: 200, height: 200 }),
			createElement('h4', { innerText: userName }),
			buttonReady = createButtonGreen('READY', () => {
				buttonReady.style.backgroundColor = '#0ccf0c';
				buttonReady.innerText = 'OK';
				console.log("READY button clicked");
				SendEvent('start_game');

			})
		);
		return playerInfo;
	}

	function drawLobbyLocal() {
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'LOCAL MATCH' }),
			createElement('h3', { innerText: 'LOBBY', style: 'margin-bottom: 20px;' }),
			createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				drawPlayerLocal('Player1'),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				drawPlayerLocal('Player2')
			),
			createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				createButton('BACK', () => {
					document.querySelector('.menu').remove();
					drawMainMenu()
				}),
				createButtonGreen('START', () => {
					document.querySelector('.menu').remove();
					//StartGame('local');
				})
			)
		);
		document.querySelector('.pong-container').appendChild(lobbyMenu);
	}

	function drawPlayerLocal(name) {
		const playerInfo = createElement('div', { className: 'button-vertical' },
			createElement('h4', { innerText: name }),
		);

		if (name === 'Player1') {
			const info = createElement('div', { className: 'button-vertical' },
				createElement('img', { src: '/static/img/avatarDefault.gif', width: 200, height: 200 }),
				createElement('h4', { innerText: 'Controls' }),
				createElement('h4', { innerText: 'up: W / down: S', style: 'margin-bottom: 30px;' }),
			);
			playerInfo.appendChild(info);
		}
		else {
			const info = createElement('div', { className: 'button-vertical' },
				createElement('img', { src: '/static/img/avatarDefault.gif', width: 200, height: 200, style: 'transform: scaleX(-1);' }),
				createElement('h4', { innerText: 'Controls' }),
				createElement('h4', { innerText: 'up:	⬆ / down:	⬇' }),
			);
			playerInfo.appendChild(info);
		}

		return playerInfo;
	}

	function drawTournament() {
		const onlineMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'TOURNAMENT' }),
			createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
			createElement('div', { className: 'button-vertical' },
				createButton('CREATE TOURNAMENT', () => {
					onlineMenu.remove();
					console.log("CREATE TOURNAMENT button clicked")
					// ConnectWebsocket('normal', userName);
					drawLobbyTournament('create');
				}),
				createButton('JOIN TOURNAMENT', () => {
					onlineMenu.remove();
					// Need to change so it only joins
					// CloseWebsocket();
					// ConnectWebsocket('normal', userName);
					drawLobbyTournament('join');
				}),
				createButton('BACK', () => {
					onlineMenu.remove();
					drawMainMenu();
				})
			)
		);
		document.querySelector('.pong-container').appendChild(onlineMenu);
	}

	function drawLobbyTournament(mode) {
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'TOURNAMENT' }),
			createElement('h3', { innerText: 'LOBBY', style: 'margin-bottom: 20px;' }),
		);

		let player1Info;
		let player2Info;
		let player3Info;
		let player4Info;

		if (mode === 'create') {
			let playerInfo = createElement('div', { className: 'button-vertical' },
				player1Info = drawPlayerTournament(userName, 1),
				createElement('hr', { style: 'width: 100%;' }),
				player2Info = drawPlayerTournament('waiting', 2),
				createElement('hr', { style: 'width: 100%;' }),
				player3Info = drawPlayerTournament('waiting', 3),
				createElement('hr', { style: 'width: 100%;' }),
				player4Info = drawPlayerTournament('waiting', 4),

			);
			lobbyMenu.appendChild(playerInfo);
		}
		// else {
		// 	var [user1, user2 ] = GetUsers();
		// 	console.log('userName: ' + userName + ' | user1: ' + user1 + ' | user2: ' + user2);

		// 	let playerInfo = createElement('div', { className: 'button-vertical', style: 'align-items: flex-start;' },
		// 		player1Info = drawPlayerTournament(user1),
		// 		createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
		// 		player2Info = drawPlayerTournament(userName),
		// 	);
		// 	lobbyMenu.appendChild(playerInfo);
		// }

		const backButton = createButton('BACK', () => {
			document.querySelector('.menu').remove();
			drawTournament();
		});
		backButton.style.marginTop = '40px';
		lobbyMenu.appendChild(backButton);

		document.querySelector('.pong-container').appendChild(lobbyMenu);
	}

	function drawPlayerTournament(userName, position) {
		if (userName === 'waiting') {
			const playerInfo = createElement('div', { className: 'button-horizontal', style: 'height: 50px;' },
				createElement('h4', { innerText: 'Player' + position + ': ' }),
				createElement('h4', { innerText: 'Waiting for a player', style: 'width: 300px;' }),
				createElement('div', { style: 'width: 100px;' },
					createElement('img', { src: '/static/img/loading.gif', width: 30, height: 30 })
				)
			);
			return playerInfo;
		}

		let buttonReady;

		const playerInfo = createElement('div', { className: 'button-horizontal', style: 'height: 50px;' },
			createElement('h4', { innerText: 'Player' + position + ': ' }),
			createElement('h4', { innerText: userName, style: 'width: 300px;' }),
			createElement('div', { style: 'width: 100px;' },
				buttonReady = createButtonGreen('READY', () => {
					buttonReady.style.backgroundColor = '#0ccf0c';
					buttonReady.innerText = 'OK';
					console.log("READY button clicked");
					// SendEvent('start_game');
				})
			)
		);
		return playerInfo;
	}




	drawMainMenu();
}

// initPong();
