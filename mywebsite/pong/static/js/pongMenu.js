import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';
import { ConnectWebsocket, CloseWebsocket, SendEvent, UpdatePlayerInfo, UpdateMenu } from './pong.js';
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
	else if (event.key === 'c')
		SendEvent('create_lobby', userName, TOURNAMENT_MODE);
	else if (event.key === 'j')
		SendEvent('join_lobby', userName, 'admin');
	else if (event.key === 'k')
		SendEvent('player_ready', userName, null);
	});

	drawMainMenu();
}

export function cleanupPongMenu()
{
    const menu = document.querySelector('.menu');
    if (menu)
        menu.remove();
	// Maybe use UpdateMenu()
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
				StartLocalGame();
			}),
			createButton('TOURNAMENT', () => {
				mainMenu.remove();
				ConnectWebsocket(TOURNAMENT_MODE, userName, avatar);
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
				//
				SendEvent('create_lobby', userName, NORMAL_MODE)
				drawLobbyMenu('create');
				UpdateMenu(lobbyMenu);
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
			//joinlobby on websocket
			lobbyMenu.remove();
			SendEvent('join_lobby', userName, lobbyCode);
			// after successful drawLobbyMenu('join')
			drawLobbyMenu('join');
			UpdateMenu(lobbyMenu);
		}),
	);

	const backButton = createButton('BACK', () => {
		document.querySelector('.menu').remove();
		drawOnlineMenu();
	});
	lobbyMenu.appendChild(backButton);

	document.querySelector('.pong-container').appendChild(lobbyMenu);
}

export function drawLobbyMenu(mode) {
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
		UpdateMenu(lobbyMenu);

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
        SendEvent('leave_lobby', userName)
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
			SendEvent('player_ready', userName, null);
		})
	);
	return playerInfo;
}
