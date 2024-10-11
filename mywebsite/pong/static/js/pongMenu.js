import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket, CloseWebsocket, SendEvent, UpdatePlayerInfo } from './pong.js';
import { StartLocalGame } from './pongLocal.js'

const NORMAL_MODE = 'normal';
const TOURNAMENT_MODE = 'tournament';
var lobbyMenu;
var avatar, userName;

export function initPongMenu(username, userAvatar) {

    if (userAvatar)
	    avatar = userAvatar;
    if (username)
	    userName = username;
	console.log('Pong game initialized - user:', userName);

	document.body.addEventListener( 'keydown', function(event) {
	if (event.key === 't')
		SendEvent('debug_print', userName)
	// else if (event.key === 'c')
	// 	SendEvent('create_lobby', userName, TOURNAMENT_MODE);
	// else if (event.key === 'j')
	// 	SendEvent('join_lobby', userName, 'admin');
	// else if (event.key === 'k')
	// 	SendEvent('player_ready', userName, null);
	});

	drawMainMenu();
}

export function cleanupPongMenu()
{
    const menu = document.querySelector('.menu');
    if (menu)
        menu.remove();
	avatar = null;
    userName = null;
}

function drawMainMenu() {
	const mainMenu = createElement('div', { className: 'menu' },
		createElement('h1', { innerText: 'PUSHEEN\nPONG' }),
		createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
		createElement('div', { className: 'button-vertical' },
			createButton('ONLINE MATCH', () => {
				mainMenu.remove();
				ConnectWebsocket(NORMAL_MODE, userName, avatar);
				drawOnlineMenu();
			}),
			createButton('LOCAL MATCH', () => {
				mainMenu.remove();
				drawLobbyLocal();
			}),
			createButton('TOURNAMENT', () => {
				mainMenu.remove();
				ConnectWebsocket(TOURNAMENT_MODE, userName, avatar);
				drawTournament();
			})
		)
	);
	document.querySelector('.pong-container').appendChild(mainMenu);
}

export function drawOnlineMenu() {
	const onlineMenu = createElement('div', { className: 'menu' },
		createElement('h2', { innerText: 'ONLINE MATCH' }),
		createElement('h3', { innerText: 'CHOOSE AN OPTION' }),
		createElement('div', { className: 'button-vertical' },
			createButton('CREATE LOBBY', () => {
				onlineMenu.remove();
				SendEvent('create_lobby', userName, NORMAL_MODE);
				drawLobbyOnline('create');
				// UpdateMenu(lobbyMenu);
			}),
			createButton('JOIN LOBBY', () => {
				onlineMenu.remove();
				drawJoinMenu(NORMAL_MODE);
			}),
			createButton('BACK', () => {
				onlineMenu.remove();
				CloseWebsocket();
				drawMainMenu();
			})
		)
	);
	document.querySelector('.pong-container').appendChild(onlineMenu);
}

function drawJoinMenu(mode) {
	let buttonJoin;
	lobbyMenu = createElement('div', { className: 'menu' },
		createElement('h2', { innerText: 'Enter lobby code' }),
		createElement('input', { type: 'text', id: 'inputField', name: 'inputField', placeholder: 'Enter lobby code' }),
		buttonJoin = createButton('JOIN', () => {
			const lobbyCode = document.getElementById('inputField').value;
			lobbyMenu.remove();
			SendEvent('join_lobby', userName, lobbyCode);
			// after successful drawLobbyMenu('join')
			// HERE --> rework UpdateMenu:
			// Cleaner and just better
			if (mode === NORMAL_MODE)
				drawLobbyOnline('join');
			else
				drawLobbyTournament('join');
			// UpdateMenu(lobbyMenu);
		}),
	);

	const backButton = createButton('BACK', () => {
		document.querySelector('.menu').remove();
		drawOnlineMenu();
	});
	lobbyMenu.appendChild(backButton);

	document.querySelector('.pong-container').appendChild(lobbyMenu);
}

export function drawLobbyOnline(mode) {
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
			player1Info = drawPlayerOnline(userName),
			createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
			player2Info = drawPlayerOnline('waiting'),
		);
		UpdatePlayerInfo(player1Info, player2Info);
		// UpdateMenu(lobbyMenu);

		lobbyMenu.appendChild(playerInfo);
	}
	if (mode === 'join') {

		let playerInfo = createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;' },
			player1Info = drawPlayerOnline('waiting'),
			createElement('h3', { innerText: 'VS', style: 'margin: 40px; margin-top: 100px;' }),
			player2Info = drawPlayerOnline(userName),
		);
		UpdatePlayerInfo(player1Info, player2Info);
		lobbyMenu.appendChild(playerInfo);
	}

	const backButton = createButton('BACK', () => {
		document.querySelector('.menu').remove();
        SendEvent('leave_lobby', userName)
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
		createElement('img', { src: avatar, width: 200, height: 200 }),
		createElement('h4', { innerText: userName }),
		buttonReady = createButtonGreen('READY', () => {
			buttonReady.style.backgroundColor = '#0ccf0c';
			buttonReady.innerText = 'OK';
			// UpdateMenu(lobbyMenu);
			SendEvent('player_ready', userName, null);
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
				StartLocalGame();
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
				SendEvent('create_lobby', userName, TOURNAMENT_MODE);
				drawLobbyTournament('create');
				// TODO: rework UpdateMenu();
			}),
			createButton('JOIN TOURNAMENT', () => {
				onlineMenu.remove();
				drawJoinMenu(TOURNAMENT_MODE);
				// drawLobbyTournament('join');
			}),
			createButton('BACK', () => {
				onlineMenu.remove();
				CloseWebsocket();
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
