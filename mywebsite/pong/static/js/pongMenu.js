import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket, StartGameEvent } from './pong.js';

export function initPong(userName) {
	// let user = 'userName';
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
					// FOR DEVELOPMENT
					console.log("CREATE LOBBY button clicked")
					ConnectWebsocket('normal', userName);
					// 
					drawLobbyMenu('create');
				}),
				createButton('JOIN LOBBY', () => {
					onlineMenu.remove();
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
		const lobbyMenu = createElement('div', { className: 'menu' },
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
				console.log("READY button clicked")
				StartGameEvent();
			})
		);
		return playerInfo;
	}




		drawMainMenu();
}

// initPong();
