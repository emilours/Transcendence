import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket } from './pong.js';

export function initPong(userName) {
	this.userName = userName;
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
			createElement('h3', { innerText: 'LOBBY' })
		);

		let player1Info;
		let player2Info;

		if (mode === 'create') {
			let playerInfo = createElement('div',
				createElement('h3', { innerText: this.userName }),
				createElement('h3', { innerText: ' VS ' }),
				player2Info = createElement('h3', { innerText: 'Waiting for player...' })
			);
			lobbyMenu.appendChild(playerInfo);
		}





		document.querySelector('.pong-container').appendChild(lobbyMenu);

	}


	drawMainMenu();
}

// initPong();
