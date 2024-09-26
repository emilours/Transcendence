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
				}),
				createButton('TOURNAMENT', () => {
					mainMenu.remove();
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
					//
					ConnectWebsocket('normal', userName);
					drawLobbyMenu('create');
				}),
				createButton('JOIN LOBBY', () => {
					onlineMenu.remove();
					// Need to change so it only joins
					ConnectWebsocket('normal', userName);
					drawLobbyMenu('join');
				}),
				createButton('BACK', () => {
					onlineMenu.remove();
					drawMainMenu();
				})
			)
		);
		document.querySelector('.pong-container').appendChild(onlineMenu);
	}

	function drawLobbyMenu(mode) {
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'ONLINE MATCH' }),
			createElement('h3', { innerText: 'LOBBY', style: 'margin-bottom: 20px;' }),
		);

		let player1Info;
		let player2Info;

		if (mode === 'create') {
			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerInfo(userName),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerInfo('waiting'),
			);
			lobbyMenu.appendChild(playerInfo);
		}
		if (mode === 'join') {
			var [user1, user2 ] = GetUsers();
			console.log('userName: ' + userName + ' | user1: ' + user1 + ' | user2: ' + user2);

			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerInfo(user1),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerInfo(userName),
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

	function drawPlayerInfo(userName) {
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
				console.log("lobby: ", lobbyMenu);
				SendEvent('player_ready', lobbyMenu);
				// SendEvent('start_game', lobbyMenu);

			})
		);
		return playerInfo;
	}




		drawMainMenu();
}

// initPong();
