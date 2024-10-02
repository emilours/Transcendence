import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket, CloseWebsocket, SendEvent, UpdatePlayerInfo, UpdateMenu } from './pong.js';
import { StartLocalGame } from './pongLocal.js'

export function initPong(userName, avatar) {
	// let user = 'userName';
	let lobbyMenu;
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
					StartLocalGame();
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
					ConnectWebsocket('normal', userName, avatar);
					drawLobbyMenu('create');
					UpdateMenu(lobbyMenu);
				}),
				createButton('JOIN LOBBY', () => {
					onlineMenu.remove();
					// Need to change so it only joins
					ConnectWebsocket('normal', userName, avatar);
					drawJoinMenu();
					// UpdateMenu(lobbyMenu);
				}),
				createButton('BACK', () => {
					onlineMenu.remove();
					drawMainMenu();
				})
			)
		);
		document.querySelector('.pong-container').appendChild(onlineMenu);
	}

	function drawJoinMenu() {
		let buttonJoin;
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'Enter lobby code' }),
			createElement('input', { type: 'text', id: 'inputField', name: 'inputField', placeholder: 'Enter lobby code' }),
			buttonJoin = createButton('JOIN', () => {
				const lobbyCode = document.getElementById('inputField').value;
				UpdateMenu(lobbyMenu);
				//joinlobby on websocket
				SendEvent('join_lobby', lobbyCode);
				// after successful drawLobbyMenu('join')
				// drawLobbyMenu('join');
			}),
		);

		const backButton = createButton('BACK', () => {
			document.querySelector('.menu').remove();
			drawOnlineMenu();
		});
		lobbyMenu.appendChild(backButton);

		document.querySelector('.pong-container').appendChild(lobbyMenu);
	}

	function drawLobbyMenu(mode) {
		let lobbyCode = createElement('h4', {innerText: '', style: 'co'});
		lobbyMenu = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'ONLINE MATCH' }),
			createElement('h3', { innerText: 'LOBBY CODE', style: 'margin-bottom: 20px;' }),
			createElement('div', {
				style: `
					font-size: 1em;
					padding: 5px;
					text-align: center;
					color: black;
					display: inline-block;
					background-color: rgba(0.9, 0.9, 0.9, 0.7);
					width: fit-content;
				`
			}, lobbyCode)
		);

		let player1Info;
		let player2Info;

		if (mode === 'create') {
			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerInfo(userName, avatar),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerInfo('waiting'),
			);
			UpdatePlayerInfo(player1Info, player2Info);

			lobbyMenu.appendChild(playerInfo);
		}
		if (mode === 'join') {

			let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
				player1Info = drawPlayerInfo('waiting'),
				createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
				player2Info = drawPlayerInfo(userName),
			);
			UpdatePlayerInfo(player1Info, player2Info);
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
			createElement('img', { src: avatar, width: 200, height: 200 }),
			createElement('h4', { innerText: userName }),
			buttonReady = createButtonGreen('READY', () => {
				buttonReady.style.backgroundColor = '#0ccf0c';
				buttonReady.innerText = 'OK';
				console.log("lobby: ", lobbyMenu);
				UpdateMenu(lobbyMenu);
				SendEvent('player_ready', null);
			})
		);
		return playerInfo;
	}




		drawMainMenu();
}

// initPong();
