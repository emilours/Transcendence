import * as THREE from './three.module.js';
import { OrbitControls } from './OrbitControls.js';
import { TextGeometry } from './TextGeometry.js';
import { FontLoader } from './FontLoader.js';

import { drawOnlineMenu, drawLobbyOnline, drawLobbyTournament, initPongMenu, createButtonReady, drawTournament } from './pongMenu.js';
import { createElement } from './GameUtils.js';
import { DrawGameOverlay, DrawLocalGameOverlay, DrawGameHud, DrawLocalGameHud, RemoveMenu} from './HudOverlay.js';


const PADDLE_SPEED = 8.0;
const PADDLE_WIDTH = 0.2;
const BALL_SPEED = 2.0;
const BALL_SIZE = 0.2;
const MAX_HEIGHT = 4.5;
const MIN_HEIGHT = -4.5;
const LOADING_IMG = '/static/img/loading.gif';
const WAITING_FOR_PLAYER = 'Waiting for a player';
const PLAYER_IMG_SIZE = 200;
const LOADING_IMG_SIZE = 70;
const TOURNAMENT_LOADING_IMG_SIZE = 30;
const PLAYER_READY = 1;
const NORMAL_CHECKMARK_SIZE = 50;
const TOURNAMENT_CHECKMARK_SIZE = 30;
const TOURNAMENT_MODE = 'tournament';
const NORMAL_MODE = 'normal';


var scene, camera, renderer, controls;
var ballTexture;
var VIEW_ANGLE = 45, ASPECT = 16 / 9, NEAR = 0.1, FAR = 2000;


// custom global variables
var light, line, ball, ballBB, leftPaddle, leftPaddleOutLine, leftPaddleBB, rightPaddle, rightPaddleOutLine, rightPaddleBB, keys, scoreMesh;
var arenaFloor, arenaLeftSide, arenaTopSide, arenaRightSide, arenaBottomSide;
var userName;
var socket;
// var scoreGeometry, scoreFont;
var ballSpeed = {x: BALL_SPEED, y: BALL_SPEED};
var leftPlayerScore = 0; // player 1
var rightPlayerScore = 0; // player 2
var running = true;
var lastTime = 0;
var deltaTime = 0;

export function InitThreeJS()
{
	// THREEJS basic const global variables
	scene = new THREE.Scene();
	scene.background = new THREE.Color(0xa400bd);

	camera =  new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
	camera.position.set(0, -11, 13);
	camera.lookAt(0, 0, 0);
	scene.add(camera);

	renderer = new THREE.WebGLRenderer({ antialias: true, canvas: game});
	renderer.setPixelRatio(window.devicePixelRatio);
	renderer.setSize(window.innerWidth, window.innerHeight);
	renderer.outputEncoding = THREE.sRGBEncoding;
	document.getElementById('pong-container-id').appendChild(renderer.domElement);

    // Create and set up OrbitControls
    controls = new OrbitControls(camera, renderer.domElement);

	// Loading Ball texture
    //NOTE: either font or textures causes 'GPU stall due to ReadPixels'
	const textureLoader = new THREE.TextureLoader();
	ballTexture = textureLoader.load("../../static/textures/ball_texture.png");

	// Loading font for 3D text
	// const loader = new FontLoader();
	// loader.load( '../../static/fonts/roboto_condensed.json', function ( font ) {
	// 	scoreFont = font;

		// createScoreText();
	// });

}

function createReadyCheckmark(size)
{
	const svgNS = "http://www.w3.org/2000/svg"; // SVG namespace

	const readySquare = createElement('div', {className: 'ready-square'});

	const readyCheckmark = createElement('div', {className: 'ready-checkmark'});

	// Create the SVG element with correct namespace
	const svgElement = createElementNS(svgNS, 'svg', {
		width: size,  // Adjust the size for debugging
		height: size,
		viewBox: '0 0 24 24',
		// style: 'border: 1px solid red;' // Add a border to visually debug
	});

	// Create the path element with correct namespace
	const pathElement = createElementNS(svgNS, 'path', {
		d: 'M20.285 2l-11.285 11.567-5.286-5.011-3.714 3.716 9 8.728 15-15.285z',
		fill: 'green'  // Ensure the path has a visible color
	});

	svgElement.appendChild(pathElement);
	readyCheckmark.appendChild(svgElement);
	readySquare.appendChild(readyCheckmark);
	return (readySquare);

}

function createElementNS(namespace, type, properties = {}, ...children) {
	const element = document.createElementNS(namespace, type);

	// Object.assign(element, properties);
    //What it does: This method directly assigns properties to the element object. This works for standard DOM element properties (e.g., id, className, textContent, onclick, etc.).
    //Behavior: Object.assign sets the properties of the element as object properties, not as attributes. This means it modifies the JavaScript object representation of the element rather than setting HTML attributes directly.
    //Use Case: It's best for setting DOM object properties rather than attributes.

    for (let property in properties)
    {
        element.setAttribute(property, properties[property]);
    }
    //What it does: This method explicitly sets attributes on the DOM element. This is the way to add standard HTML attributes (like class, data-* attributes, etc.) to the element's markup.
    //Use Case: Use this when you need to set HTML attributes that are visible in the markup, including custom or non-standard attributes (like data- attributes).
    //Behavior: The setAttribute method sets an attribute directly on the HTML element itself, meaning the attribute will be visible in the HTML and DOM tree. It only applies to attributes, not properties.

	children.forEach(child => element.appendChild(child));
	return element;
}


// 'button' --> button type (same as 'div')
// '.button' --> button className

function UpdateLobbyOnline(user, avatar, ready, playerInfo)
{

	let img_size = PLAYER_IMG_SIZE;
	if (user == undefined)
		user = WAITING_FOR_PLAYER;
	if (avatar == undefined)
	{
		avatar = LOADING_IMG;
		img_size = LOADING_IMG_SIZE;
	}
	if (playerInfo)
	{
		const playerUsername = playerInfo.querySelector('h4');
		if (playerUsername) {
			playerUsername.innerText = user;
		}
		const playerImage = playerInfo.querySelector('img');
		if (playerImage) {
			playerImage.src = avatar;
			playerImage.width = img_size;
			playerImage.height = img_size;
			if (img_size == PLAYER_IMG_SIZE)
				playerImage.removeAttribute('style');
			else
				playerImage.style.margin = '65px';
		}

		let readyCheckmark = playerInfo.querySelector('.ready-square');
		if (readyCheckmark)
		{
			playerInfo.removeChild(readyCheckmark);
			readyCheckmark.remove();
		}
		let readyButton = playerInfo.querySelector('.button.green');
		if (!readyButton && user == userName)
		{
			readyButton = createButtonReady();
			playerInfo.appendChild(readyButton);
		}
		else if (user != userName)
		{
			if (readyButton)
			{
				playerInfo.removeChild(readyButton);
				readyButton.remove();
			}
			if (ready == PLAYER_READY)
			{
				const readyCheckmark = createReadyCheckmark(NORMAL_CHECKMARK_SIZE);
				playerInfo.appendChild(readyCheckmark);
			}
		}
	}
}


function UpdateLobbyTournament(user, avatar, ready, playerInfo)
{
	// console.log(userName, "update: ", user);
	if (!playerInfo)
		return;
	if (user == undefined)
		user = WAITING_FOR_PLAYER;

	const playerUsername = playerInfo.querySelectorAll('h4');
	if (playerUsername[1]) {
		playerUsername[1].innerText = user;
	}

	const playerDiv = playerInfo.querySelector('div');

	let readyButton = playerDiv.querySelector('button');

	let loadingImg = playerDiv.querySelector('img');
	let readyCheckmark = playerDiv.querySelector('.ready-square');
	if (readyCheckmark)
	{
		playerDiv.removeChild(readyCheckmark);
		readyCheckmark.remove();
	}

	if (user == WAITING_FOR_PLAYER) // 'Waiting for a player' + 'loading.gif'
	{
		if (readyButton)
		{
			playerDiv.removeChild(readyButton);
			readyButton.remove();
		}
		if (!loadingImg)
		{
			loadingImg = createElement('img', { src: LOADING_IMG, width: TOURNAMENT_LOADING_IMG_SIZE, height: TOURNAMENT_LOADING_IMG_SIZE});
			playerDiv.appendChild(loadingImg);
		}
	}
	else // username + empty OU username + 'READY' OU username + checkmark
	{
		if (loadingImg)
		{
			playerDiv.removeChild(loadingImg);
			loadingImg.remove();
		}
		if (!readyButton && user == userName)
		{
			readyButton = createButtonReady();
			playerDiv.appendChild(readyButton);
		}
		else if (readyButton && user != userName)
		{
			playerDiv.removeChild(readyButton);
			readyButton.remove();
		}
		if (!readyButton && ready == PLAYER_READY)
		{
			readyCheckmark = createReadyCheckmark(TOURNAMENT_CHECKMARK_SIZE);
			playerDiv.appendChild(readyCheckmark);
		}
	}
}

// FUNCTIONS TO TIGGER EVENT ON SOCKET.IO SERVER
export function SendEvent(event, username, data, gameMode)
{
    userName = username;
	// console.log("Sending event:", event, "username:", username, "data:", data);
    try
    {
        if (!socket || !socket.connected)
        {
            // console.log("Socket.io connection not open");
            return false;
        }
		if (event == "join_lobby")
		{
			socket.emit(event, username, data, gameMode);
		}
        else if (username == null && data == null)
            socket.emit(event);
        else if (username == null)
            socket.emit(event, data);
        else if (data == null)
            socket.emit(event, username);
        else
            socket.emit(event, username, data);
    }
    catch (error)
    {
        // console.log("catch: " + error);
        const activeMenu = document.querySelector('.menu');
        if (activeMenu)
            activeMenu.remove();
        initPongMenu(username, null);
    }
	return true;
}


export function ConnectWebsocket(type, username)
{
	// WEBSOCKET
	running = true;
	userName = username;
	leftPlayerScore = 0;
	rightPlayerScore = 0;
	InitCustomAlerts();
	if (socket && socket.connected) {
        socket.disconnect();  // Disconnect the existing socket
        // console.log('Existing socket disconnected');
    }

	// ${window.location.host}
	socket = io(`wss://${window.location.hostname}:6789`, {
		transports: ['websocket'],  // Use only WebSocket transport
		secure: true,
		reconnection: false, // Disable reconnection to observe disconnection behavior
		query: {
			username: username,  // Pass username in the query string
			gameType: type   // Pass game type in the query string
		}
	});

	socket.on("connect", function() {
		// console.log("Connected to socket.io");
	});
	socket.on("message", function(message) {
		// console.log("Message from server: ", message);
	});

	// DISCONNECT/ERROR EVENTS
	socket.on("disconnect", function(reason) {
		// console.log("Disconnected from socket.io for: " + reason);
		running = false;
	});
	// Handle connection errors
    socket.on('connect_error', (error) => {
        // console.error('Connection failed:', error);
    });
    // Handle other socket errors
    socket.on('error', (error) => {
        // console.error('Socket error:', error);
    });
    // Monitor reconnection attempts and failures
    socket.on('reconnect_attempt', () => {
        // console.log('Attempting to reconnect...');
    });
    socket.on('reconnect_failed', () => {
        // console.error('Reconnection failed after multiple attempts.');
    });

	// CUSTOM EVENTS
	socket.on('client_count', function(count) {
        // if (count <= 1)
		//     console.log(count + " client connected");
        // else
		//     console.log(count + " clients connected");

    });
	socket.on('user_joined', function(user) {
		// console.log("User " + user + " has joined a lobby.");
	});
	socket.on('user_left', function(user) {
		// console.log("User " + user + " has left a lobby.");
	});
	socket.on('game_ready', function() {
		// console.log("BOTH PLAYER READY");
        const activeMenu = document.querySelector('.menu');
        if (activeMenu)
			activeMenu.remove();
		// TODO: maybe need to add event from server 'init_game' for tournament (2 players play game, 2 stay in waiting room ?)
		// HERE: either cleanup works or just send the event to the person that left
		Cleanup();
		StartGame("online");
		SendEvent('start_game', userName);
	});
	socket.on('invalid_lobby_code', function(gameMode) {
        const activeMenu = document.querySelector('.menu');
        if (activeMenu)
            activeMenu.remove();
		if (gameMode == NORMAL_MODE)
       		drawOnlineMenu();
		else
			drawTournament();
		CustomAlert("Invalid Lobby Code");
	});
	socket.on('player_already_in_room', function (index) {
		// console.log("player already in room, player index:", index);
		const activeMenu = document.querySelector('.menu');
        if (activeMenu)
		{
			let mode;
			activeMenu.remove();
			if (index == 0)
				mode = 'create';
			else if (index == 1)
				mode = 'join';
			drawLobbyOnline(mode);
		}
		CustomAlert("You already are in a game, joining lobby...");
	});
	socket.on('invalid_game_mode', function(gameMode) {
		const activeMenu = document.querySelector('.menu');
		if (activeMenu)
			activeMenu.remove();
		if (gameMode == NORMAL_MODE)
			drawOnlineMenu();
		else
			drawTournament();
		CustomAlert("Invalid Game Mode");
	});
	socket.on('room_already_full', function(gameMode) {
		const activeMenu = document.querySelector('.menu');
		if (activeMenu)
			activeMenu.remove();
		if (gameMode == NORMAL_MODE)
			drawOnlineMenu();
		else
			drawTournament();
		CustomAlert("Room Already Full");
	});


	socket.on('send_lobby_data', function(data) {
		const lobbyCode = data.lobby_id;
		const maxLobbySize = data.max_lobby_size;
		const gameType = data.game_type;
		// console.log("lobby:", lobbyCode, "is a", gameType, "game");

        const activeMenu = document.querySelector('.menu');
		if (activeMenu)
		{
                const codeText = activeMenu.querySelector('h4');
                if (codeText)
                    codeText.innerText = "code: " + lobbyCode;
		}
		if (!activeMenu)
			return

		const playerInfoNormal = document.querySelectorAll('.button-vertical');
		const playerInfoTournament = document.querySelectorAll('.button-horizontal');
		for (let i = 0; i < maxLobbySize; i++)
		{
			if (gameType == TOURNAMENT_MODE)
				UpdateLobbyTournament(data.users[i], data.avatars[i], data.ready[i], playerInfoTournament[i]);
			else
				UpdateLobbyOnline(data.users[i], data.avatars[i], data.ready[i], playerInfoNormal[i]);
		}
	});

    socket.on('player_reconnect', function(data) {
        const user = data.username;
        const lobbyId = data.lobby_id;
        const gameType = data.game_type;
        let menu = document.querySelector('.menu');
        if (menu)
            menu.remove(); // removeChild ?
        if (gameType == NORMAL_MODE)
            drawLobbyOnline('reconnect');
        else if (gameType == TOURNAMENT_MODE)
            drawLobbyTournament('reconnect');
		CustomAlert("You were in a game, joining lobby...");
    });
	//HERE
	socket.on('update_overlay', function(data) {
		const text = data.text;
		const winner = data.winner;
		const gameOver = data.game_over;
		const avatar = data.avatar;
		const gameType = data.game_type;
        RemoveMenu('.overlay');
		if (text == '')
            return;
        let mode;
        if (gameOver == 1)
            mode = 'gameover';
        else
            mode = 'waiting';
        DrawGameOverlay(mode, text, avatar, userName, winner);
	});
	socket.on('refresh', function() {
		const customAlert = document.getElementById('customAlert');
		customAlert.style.display = 'none';
		RemoveMenu('.menu');
		RemoveMenu('.game-hud');
		RemoveMenu('.overlay');
		Cleanup();
		CloseWebsocket();
		initPongMenu();
	});
}

export function CloseWebsocket() {
	if (socket && socket.connected) {
		socket.disconnect();
		// console.log("Socket.IO connection closed");
	}
	running = false;
}

function CustomAlert(alertMessage)
{
	const customAlert = document.getElementById('customAlert');
	if (customAlert)
	{
		const customAlertText = customAlert.querySelector('p');
		if (customAlertText)
		{
			customAlertText.innerText = alertMessage;
			customAlert.style.display = 'block';
		}
	}
}

function InitCustomAlerts()
{
	// Get elements
	const customAlert = document.getElementById('customAlert');
	const closeAlert = document.getElementById('closeButton');
	const alertOkBtn = document.getElementById('OkButton');

	// Close the alert when the "X" is clicked
	closeAlert.onclick = function () {
	customAlert.style.display = 'none';
	};

	// Close the alert when the "OK" button is clicked
	alertOkBtn.onclick = function () {
	customAlert.style.display = 'none';
	};

	// Close the alert when clicking outside the modal content
	window.onclick = function (event) {
	if (event.target === customAlert) {
		customAlert.style.display = 'none';
	}
};
}

function onWindowResize()
{
	const width = window.innerWidth;
	const height = window.innerHeight;

	// camera.aspect = 16 / 9;
	// camera.updateProjectionMatrix();

	// might need to change so it's not fullscreen
	renderer.setSize( width, height );
	// console.log("Window Resized!");
	// console.log("width: " + width + " height: " + height);
}

export function StartGame(mode)
{
	Init();
	if (mode === "local")
		StartLocalGame();
	else if (mode === "online")
		StartOnlineGame();
}

function StartOnlineGame()
{
    let firstDraw = 1;
	socket.on('game_update', function(data) {
        if (firstDraw == 1)
        {
			RemoveMenu('.game-hud');
            DrawGameHud(userName, data.usernames, data.avatars, data.scores);
            firstDraw = 0;
            return;
        }
		ball.position.x = parseFloat(data.ballPosition[0]);
		ball.position.y = parseFloat(data.ballPosition[1]);
		leftPaddle.position.y = parseFloat(data.pos[0]);
		rightPaddle.position.y = parseFloat(data.pos[1]);
		let player1Score = parseFloat(data.scores[0]);
		let player2Score = parseFloat(data.scores[1]);

		if (player1Score != leftPlayerScore || player2Score != rightPlayerScore)
		{
			leftPlayerScore = player1Score;
			rightPlayerScore = player2Score;
			// createScoreText();
            RemoveMenu('.game-hud');
            DrawGameHud(userName, data.usernames, data.avatars, data.scores);
		}
    });
	OnlineLoop();
}

function StartLocalGame()
{
	let firstDraw = 1;
	if (firstDraw == 1)
	{
		RemoveMenu('.game-hud');
		DrawLocalGameHud([leftPlayerScore, rightPlayerScore]);
		firstDraw = 0;
	}
	requestAnimationFrame(LocalLoop);

}

function createScoreText()
{
	if (scoreMesh) {
		scene.remove(scoreMesh);
		scoreMesh.geometry.dispose();
		scoreMesh.material.dispose();
	}
	scoreGeometry = new TextGeometry( leftPlayerScore + "  :  " + rightPlayerScore, {
		font: scoreFont,
		size: 1,
		// !!!! Use height and not depth
		height: 0.1,
		curveSegments: 12,
		bevelEnabled: true,
		bevelThickness: 0.03,
		bevelSize: 0.02,
		bevelOffset: 0,
		bevelSegments: 5
	});

	const scoreMaterial = new THREE.MeshBasicMaterial({color: 0xffffff});
	scoreMesh = new THREE.Mesh(scoreGeometry, scoreMaterial);


	// Compute the bounding box and center the score
	scoreGeometry.computeBoundingBox();
	const scoreBoundingBox = scoreGeometry.boundingBox;
	const scoreSize = new THREE.Vector3();
	scoreBoundingBox.getSize(scoreSize);
	scoreMesh.position.x = -scoreSize.x / 2;
	scoreMesh.position.y = -scoreSize.y / 2;
	scoreMesh.position.z = -scoreSize.z / 2;

	scoreMesh.position.y += 6;
	scoreMesh.position.z += 1.5;
	scoreMesh.rotateX(45);
	scene.add(scoreMesh);
}


function HandleKeyDown(e)
{
	if (e.key === 't')
		SendEvent('debug_print', userName)
	if (e.key === "ArrowUp" || e.key === "ArrowDown")
		e.preventDefault();

	var key = e.code.replace('Key', '').toLowerCase();
	if ( keys[ key ] !== undefined )
		keys[ key ] = true;
}

function HandleKeyUp(e)
{
	var key = e.code.replace('Key', '').toLowerCase();
	if ( keys[ key ] !== undefined )
		keys[ key ] = false;
}


function Init()
{
	// reset values
	running = true;
	leftPlayerScore = 0;
	rightPlayerScore = 0;
	lastTime = 0;
	deltaTime = 0;
	// TODO: randomize this:
	ballSpeed = {x: BALL_SPEED, y: BALL_SPEED};

	// WINDOW RESIZE
	window.addEventListener( 'resize', onWindowResize );

	// LIGHT
	// can't see textures without light
	light = new THREE.PointLight(0xffffff);
	light.position.set(0, 0, 10);
	scene.add(light);

	// INPUT
	keys = {
		a: false,
		s: false,
		d: false,
		w: false,
		arrowup: false,
		arrowdown: false,
		i: false
	};

	document.body.addEventListener( 'keydown', HandleKeyDown);
	document.body.addEventListener( 'keyup', HandleKeyUp);


	// MATERIAL
	const lineMaterial = new THREE.LineDashedMaterial( { color: 0x353535, linewidth: 1, scale: 1, dashSize: 0.5, gapSize: 0.5 } );
	const paddleMaterial = new THREE.MeshBasicMaterial({ color: 0x353535 });
	const whiteMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
	const blackMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
	const paddleOutlineMaterial = new THREE.MeshBasicMaterial({ color: 0xd1d1d1, side: THREE.BackSide });
	const ballMaterial = new THREE.MeshBasicMaterial({map: ballTexture});


	// CUSTOM GEOMETRY

	// Arena
	const arenaFloorGeometry = new THREE.BoxGeometry(16, 9, 0.5);
	const arenaSmallSideGeometry = new THREE.BoxGeometry(0.5, 10, 0.5);
	const arenaLargeSideGeometry = new THREE.BoxGeometry(17, 0.5, 0.5);
	arenaFloor = new THREE.Mesh(arenaFloorGeometry, blackMaterial);
	arenaLeftSide = new THREE.Mesh(arenaSmallSideGeometry, whiteMaterial);
	arenaTopSide = new THREE.Mesh(arenaLargeSideGeometry, whiteMaterial);
	arenaBottomSide = arenaTopSide.clone();
	arenaRightSide = arenaLeftSide.clone();
	scene.add(arenaFloor);
	scene.add(arenaLeftSide);
	scene.add(arenaTopSide);
	scene.add(arenaRightSide);
	scene.add(arenaBottomSide);
	arenaFloor.position.z -= 0.5;
	arenaTopSide.position.y += 4.75;
	arenaBottomSide.position.y -= 4.75;
	arenaRightSide.position.x += 8.25;
	arenaLeftSide.position.x -= 8.25;

	// Ball
	const ballGeometry = new THREE.SphereGeometry(BALL_SIZE, 64, 32);
	ball = new THREE.Mesh(ballGeometry, ballMaterial);
	ball.position.x = 0;
	ball.position.y = 0;
	scene.add(ball);

	ballBB = new THREE.Sphere(ball.position, BALL_SIZE);


	// Paddles
	const paddleGeometry = new THREE.BoxGeometry(0.2, 2, 0.2);
	leftPaddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
	leftPaddleOutLine = new THREE.Mesh(paddleGeometry, paddleOutlineMaterial);
	rightPaddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
	rightPaddleOutLine = new THREE.Mesh(paddleGeometry, paddleOutlineMaterial);
	scene.add(leftPaddle);
	scene.add(leftPaddleOutLine);
	scene.add(rightPaddleOutLine);
	scene.add(rightPaddle);
	leftPaddle.position.x -= 7.5;
	leftPaddleOutLine.position.x = leftPaddle.position.x;
	leftPaddleOutLine.scale.multiplyScalar(1.05);
	leftPaddleOutLine.scale.x *= 1.2;
	rightPaddle.position.x += 7.5;
	rightPaddleOutLine.position.x = rightPaddle.position.x;
	rightPaddleOutLine.scale.multiplyScalar(1.05);
	rightPaddleOutLine.scale.x *= 1.2;

	leftPaddleBB = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
	leftPaddleBB.setFromObject(leftPaddle);

	rightPaddleBB = new THREE.Box3(new THREE.Vector3(), new THREE.Vector3());
	rightPaddleBB.setFromObject(rightPaddle);


	// Middle Line
	const points = [];
	points.push( new THREE.Vector3( 0, MAX_HEIGHT, -0.20 ) );
	points.push( new THREE.Vector3( 0, MIN_HEIGHT, -0.20) );
	const lineGeometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( lineGeometry, lineMaterial );
	scene.add(line);
	line.computeLineDistances();

}


function OnlineLoop()
{
	if (running == false)
		return;
	requestAnimationFrame(OnlineLoop);
	OnlineInputs();
	OnlineUpdate();
	renderer.render(scene, camera);
}

function LocalLoop(timestamp)
{
	if (lastTime == 0)
		lastTime = timestamp;
	if (running == false)
	{
		// console.log("Not running anymore!");
		return;
	}
	// requestAnimationFrame(Loop);
	LocalInputs();
	LocalUpdate(timestamp);
	renderer.render(scene, camera);
	requestAnimationFrame(LocalLoop);
}

function OnlineInputs()
{
	const inputEvent = 'pong_input'
	if (running == false)
		return;
	//DEBUG
	// if (keys.i)
	// {
	// 	console.log("[INFO]");
	// 	console.log("[right paddle] x: " + leftPaddle.position.x + " y: " + leftPaddle.position.y + " z: " + leftPaddle.position.z);
	// 	console.log("[ball] x: " + ball.position.x + " y: " + ball.position.y + " z: " + ball.position.z);
	// 	console.log("[right paddle] x: " + rightPaddle.position.x + " y: " + rightPaddle.position.y + " z: " + rightPaddle.position.z);
	// }

	//CLIENT SIDE PADDLE INPUTS
	// Maybe could rework that so it's faster (less event send) ?
	if (keys.w || keys.arrowup)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'up'
		}))
	}

	if (keys.s || keys.arrowdown)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'down'
		}))
	}
}

function LocalInputs()
{
	// DISABLE INPUT IF GAME NOT RUNNING
	if (running == false)
		return;

	// PADDLE MOVEMENT
    const paddleHeight = leftPaddle.geometry.parameters.height;
	
	// LEFT
	if (keys.w && leftPaddle.position.y + paddleHeight / 2 < MAX_HEIGHT)
        leftPaddle.position.y += PADDLE_SPEED * deltaTime; //
    else if (keys.s && leftPaddle.position.y - paddleHeight / 2 > MIN_HEIGHT)
        leftPaddle.position.y -= PADDLE_SPEED * deltaTime; //

    if (leftPaddle.position.y + paddleHeight / 2 > MAX_HEIGHT)
        leftPaddle.position.y = MAX_HEIGHT - paddleHeight / 2;
    else if (leftPaddle.position.y - paddleHeight / 2  < MIN_HEIGHT)
        leftPaddle.position.y = MIN_HEIGHT + paddleHeight / 2;


	// RIGHT
	if (keys.arrowup && rightPaddle.position.y + rightPaddle.geometry.parameters.height / 2 < MAX_HEIGHT)
        rightPaddle.position.y += PADDLE_SPEED * deltaTime; //
    else if (keys.arrowdown && rightPaddle.position.y - rightPaddle.geometry.parameters.height / 2 > MIN_HEIGHT)
        rightPaddle.position.y -= PADDLE_SPEED * deltaTime; //

    if (rightPaddle.position.y + paddleHeight / 2 > MAX_HEIGHT)
        rightPaddle.position.y = MAX_HEIGHT - paddleHeight / 2;
    else if (rightPaddle.position.y - paddleHeight / 2  < MIN_HEIGHT)
        rightPaddle.position.y = MIN_HEIGHT + paddleHeight / 2;

}

function OnlineUpdate()
{
	// Paddle Outline
	leftPaddleOutLine.position.y = leftPaddle.position.y;
	rightPaddleOutLine.position.y = rightPaddle.position.y;

    // Update controls every frame
    controls.update();
}

function LocalUpdate(timestamp)
{
	// DELTA TIME
	deltaTime = (timestamp - lastTime) / 1000;
	lastTime = timestamp;
	
	// PADDLE OUTLINE UPDATE
	leftPaddleOutLine.position.y = leftPaddle.position.y;
	rightPaddleOutLine.position.y = rightPaddle.position.y;

	// BALL - WALL COLLISION
	if (ball.position.x - BALL_SIZE <= -8)
	{
		rightPlayerScore += 1;
		// createScoreText();
		RemoveMenu('.game-hud');
		DrawLocalGameHud([leftPlayerScore, rightPlayerScore]);
		ball.position.x = 0;
		ball.position.y = 0;
	}
	if (ball.position.x + BALL_SIZE >= 8)
	{
		leftPlayerScore += 1;
		// createScoreText();
		RemoveMenu('.game-hud');
		DrawLocalGameHud([leftPlayerScore, rightPlayerScore]);
		ball.position.x = 0;
		ball.position.y = 0;
	}
	if ((ball.position.y - BALL_SIZE < MIN_HEIGHT && ballSpeed.y < 0)|| (ball.position.y + BALL_SIZE > MAX_HEIGHT && ballSpeed.y > 0))
		ballSpeed.y = -ballSpeed.y;

	// BALL10-PADDLE COLLISIONS
	leftPaddleBB.copy(leftPaddle.geometry.boundingBox).applyMatrix4(leftPaddle.matrixWorld);
    rightPaddleBB.copy(rightPaddle.geometry.boundingBox).applyMatrix4(rightPaddle.matrixWorld);
	if (ballBB.intersectsBox(rightPaddleBB) && ballSpeed.x > 0)
	{
		ballSpeed.x = -ballSpeed.x;
		ball.position.x += ballSpeed.x * (PADDLE_WIDTH / 2); //
	}
	
	if (ballBB.intersectsBox(leftPaddleBB)  && ballSpeed.x < 0)
	{
		ballSpeed.x = -ballSpeed.x;
		ball.position.x += ballSpeed.x * (PADDLE_WIDTH / 2); //
	}
	
	// BALL MOVEMENT
	ball.position.x += ballSpeed.x * BALL_SPEED * deltaTime; //
	ball.position.y += ballSpeed.y * BALL_SPEED * deltaTime; //
	ball.rotation.x += 1.5 * ballSpeed.x * deltaTime; //
	ball.rotation.y += 1.5 * ballSpeed.y * deltaTime; //

	// SCORE
	if (leftPlayerScore >= 5 || rightPlayerScore >= 5)
	{
		running = false;
		document.body.removeEventListener("keydown", function(event) {});
		// SaveMatch();
		let winner;
		if (leftPlayerScore >= 5)
			winner = "Player1";
		else
			winner = "Player2";
		DrawLocalGameOverlay(winner);

	}
}

function SaveMatch(score)
{
	fetch('/pong/SaveLocalPongMatch', {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			'X-CSRFToken': getCookie('csrftoken')
		},
		body: JSON.stringify({ score: score }),
	})
	.then(response => response.json())
	// .then(data => {
	// 	if (data.status === 'success') {
	// 		// console.log("Pong score save to database successfully!");
	// 	}
	// 	else {
	// 		console.error('Error saving score:', data.message);
	// 	}
	// })
	.catch(error => {
		// console.error('Error: ', error);
	})
}

function getCookie(name) 
{
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


export function Cleanup()
{
	running = false;
	document.body.removeEventListener( 'keydown', HandleKeyDown);
	document.body.removeEventListener( 'keyup', HandleKeyUp);
	if (scene)
	{
		scene.remove(light)
		scene.remove(arenaFloor);
		scene.remove(arenaLeftSide);
		scene.remove(arenaTopSide);
		scene.remove(arenaRightSide);
		scene.remove(arenaBottomSide);
		scene.remove(leftPaddle);
		scene.remove(leftPaddleOutLine);
		scene.remove(rightPaddleOutLine);
		scene.remove(rightPaddle);
		scene.remove(ball);
		scene.remove(line);
	}
	if (renderer)
	{
		renderer.render(scene, camera);
		renderer.clear(true, true, true);
		renderer.setSize(0, 0);
		renderer.setSize(window.innerWidth, window.innerHeight);
	}
}
