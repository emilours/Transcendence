import * as THREE from './three.module.js';
// import { OrbitControls } from './OrbitControls.js';
import { TextGeometry } from './TextGeometry.js';
import { FontLoader } from './FontLoader.js';

import { drawOnlineMenu, drawLobbyOnline, initPongMenu } from './pongMenu.js';
import { createElement, createButton, createButtonGreen, appendChildren, createArrowButton } from './GameUtils.js';

const BALL_SPEED = 0.1; //not needed i think
const BALL_SIZE = 0.2; // maybe a bit bigger
const MAX_HEIGHT = 4.5; // idk how to name this
const MIN_HEIGHT = -4.5;
const LOADING_AVATAR = '/static/img/loading.gif';
const WAITING_FOR_PLAYER = 'Waiting for a player';
const PLAYER_IMG_SIZE = 200;
const LOADING_IMG_SIZE = 70;
const TOURNAMENT_MODE = 'tournament';

// standard global variables
var scene, camera, renderer, controls, loader;

// custom global variables
var line, ball, ballBB, ballTexture, leftPaddle, leftPaddleOutLine, leftPaddleBB, rightPaddle, rightPaddleOutLine, rightPaddleBB, keys, scoreMesh;
// var overlayText;
var socket;
var userName;
var scoreGeometry, scoreFont, gameOver;

var ballSpeed = {x: BALL_SPEED, y: BALL_SPEED}; //not needed i think
var leftPlayerScore = 0; // player 1
var rightPlayerScore = 0; // player 2
var running = true;
    
function UpdateLobbyOnline(user, avatar, playerInfo)
{

	let img_size = PLAYER_IMG_SIZE;
	if (user == undefined)
		user = WAITING_FOR_PLAYER;
	if (avatar == undefined)
	{
		avatar = LOADING_AVATAR;
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
	}
}

function UpdateLobbyTournament(user, avatar, playerInfo)
{
	console.log("UpdateLobbyTournament()");
}

// FUNCTIONS TO TIGGER EVENT ON SOCKET.IO SERVER
export function SendEvent(event, username, data)
{
	console.log("Sending event:", event, "username:", username, "data:", data);
    try
    {
        if (!socket || !socket.connected)
        {
            console.log("Socket.io connection not open");
            return false;
        }
        if (username == null && data == null)
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
        console.log("catch: " + error);
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
	InitCustomAlerts();
	if (socket && socket.connected) {
        socket.disconnect();  // Disconnect the existing socket
        console.log('Existing socket disconnected');
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
		console.log("Connected to socket.io");
	});
	socket.on("message", function(message) {
		console.log("Message from server: ", message);
	});

	// DISCONNECT/ERROR EVENTS
	socket.on("disconnect", function(reason) {
		console.log("Disconnected from socket.io for: " + reason);
		running = false;
	});
	// Handle connection errors
    socket.on('connect_error', (error) => {
        console.error('Connection failed:', error);
    });
    // Handle other socket errors
    socket.on('error', (error) => {
        console.error('Socket error:', error);
    });
    // Monitor reconnection attempts and failures
    socket.on('reconnect_attempt', () => {
        console.log('Attempting to reconnect...');
    });
    socket.on('reconnect_failed', () => {
        console.error('Reconnection failed after multiple attempts.');
    });

	// CUSTOM EVENTS
	socket.on('client_count', function(count) {
        if (count <= 1)
		    console.log(count + " client connected");
        else
		    console.log(count + " clients connected");

    });
	socket.on('user_joined', function(user) {
		console.log("User " + user + " has joined a lobby.");
	});
	socket.on('user_left', function(user) {
		console.log("User " + user + " has left a lobby.");
	});
	socket.on('game_ready', function() {
		console.log("BOTH PLAYER READY");
        const activeMenu = document.querySelector('.menu');
        if (activeMenu)
			activeMenu.remove();
		// TODO: maybe need to add event from server 'init_game' for tournament (2 players play game, 2 stay in waiting room ?)
		StartGame();
		SendEvent('start_game', userName);
	});
	socket.on('invalid_lobby_code', function() {
        const activeMenu = document.querySelector('.menu');
        if (activeMenu)
            activeMenu.remove();
        drawOnlineMenu();
		CustomAlert("Invalid Lobby Code");
	});
	socket.on('player_already_in_room', function (index) {
		console.log("player already in room, player index:", index);
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

	socket.on('send_lobby_data', function(data) {
		console.log("Received data from server..");
		const lobbyCode = data.lobby_id;
		const maxLobbySize = data.max_lobby_size;
		const gameType = data.game_type;
		console.log("lobby: ", lobbyCode, "is a", gameType, "game");

        const activeMenu = document.querySelector('.menu');
		if (activeMenu && lobbyCode !== undefined)
		{
			//TODO: lobby code for normal/tournament
			const codeText = activeMenu.querySelector('h4');
			if (codeText)
				codeText.innerText = lobbyCode;
			else
				console.log("NO h4 in menu");

		}
		const playerInfoNormal = document.querySelectorAll('.button-vertical');
		const playerInfoTournament = document.querySelectorAll('.button-horizontal');
		console.log("playerInfoTournament:", playerInfoTournament);
		for (let i = 0; i < maxLobbySize; i++)
		{
			if (gameType == TOURNAMENT_MODE)
				UpdateLobbyTournament(data.users[i], data.avatars[i], playerInfoTournament[i]);
			else
				UpdateLobbyOnline(data.users[i], data.avatars[i], playerInfoNormal[i]);
		}
	});
}

export function CloseWebsocket() {
	if (socket && socket.connected) {
		socket.disconnect();
		console.log("Socket.IO connection closed");
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
	console.log("Window Resized!");
	console.log("width: " + width + " height: " + height);
}

function StartGame()
{
// TODO: I think i should load everything (all font, textures...) before initializing the rest
	Load();
	Init();
	socket.on('game_update', function(data) {
		console.log(data);
		// let data = JSON.parse(e.data);
		// console.log('Data:', data);

		if (data.ballPosition && data.ballVelocity && data.pos
			&& data.players && data.scores && typeof data.game_over !== 'undefined')
		{
			ball.position.x = parseFloat(data.ballPosition[0]);
			ball.position.y = parseFloat(data.ballPosition[1]);
			ballSpeed.x = parseFloat(data.ballVelocity[0]); //not needed i think
			ballSpeed.y = parseFloat(data.ballVelocity[1]); //not needed i think
			leftPaddle.position.y = parseFloat(data.pos[0]);
			rightPaddle.position.y = parseFloat(data.pos[1]);
			gameOver = parseInt(data.game_over);
			let player1Score = parseFloat(data.scores[0]);
			let player2Score = parseFloat(data.scores[1]);

			if (player1Score != leftPlayerScore || player2Score != rightPlayerScore)
			{
				leftPlayerScore = player1Score;
				rightPlayerScore = player2Score;
				createScoreText();
			}
		}
		// overlayText.textContent = `Ball position X: ${ball.position.x.toFixed(2)} Y: ${ball.position.y.toFixed(2)}`

	});
	Loop();
	//Cleanup();
}

function Load()
{
	// SCORE FONT
	loader = new FontLoader();
	loader.load( '../../static/fonts/roboto_condensed.json', function ( font ) {
		scoreFont = font;

		createScoreText();
	});

	// BALL TEXTURE
	const textureLoader = new THREE.TextureLoader();
	ballTexture = textureLoader.load("../../static/textures/ball_texture.png")

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

	if (gameOver == 1)
	{
		const gameOverGeometry = new TextGeometry ("GAME OVER", {
			font: scoreFont,
			size: 1.5,
			// !!!! Use height and not depth
			height: 0.2,
			curveSegments: 12,
			bevelEnabled: true,
			bevelThickness: 0.03,
			bevelSize: 0.02,
			bevelOffset: 0,
			bevelSegments: 5
		});

		const gameOverMaterial = new THREE.MeshBasicMaterial({color: 0xbd4500});
		const gameOverMesh = new THREE.Mesh(gameOverGeometry, gameOverMaterial);


		gameOverGeometry.computeBoundingBox();
		const gameOverBB = gameOverGeometry.boundingBox;
		const gameOverSize = new THREE.Vector3();
		gameOverBB.getSize(gameOverSize);
		gameOverMesh.position.x = -gameOverSize.x / 2;
		gameOverMesh.position.y = -gameOverSize.y / 2;
		gameOverMesh.position.z = -gameOverSize.z / 2;
		gameOverMesh.position.z += 3;
		scene.add(gameOverMesh);

	}

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

function Init()
{
	// SCENE
	scene = new THREE.Scene();
	scene.background = new THREE.Color(0xa400bd);

	// CAMERA
	var SCREEN_WIDTH = window.innerWidth, SCREEN_HEIGHT = window.innerHeight;
	// FIXED ASPECT RATIO Best fix so we always see the whole pong
	var VIEW_ANGLE = 45, ASPECT = 16 / 9, NEAR = 0.1, FAR = 2000;
	camera = new THREE.PerspectiveCamera(VIEW_ANGLE, ASPECT, NEAR, FAR);
	camera.position.set(0, -11, 13);
	camera.lookAt(0, 0, 0);
	scene.add(camera);

	// WINDOW RESIZE
	window.addEventListener( 'resize', onWindowResize );
	console.log("width: " + SCREEN_WIDTH + " height: " + SCREEN_HEIGHT);


	// RENDERER
	renderer = new THREE.WebGLRenderer({antialias: true, canvas: game});
	renderer.setPixelRatio( window.devicePixelRatio );
	renderer.setSize(SCREEN_WIDTH, SCREEN_HEIGHT);
	renderer.outputEncoding = THREE.sRGBEncoding;
	const container = document.getElementById('pong-container-id');
	container.appendChild(renderer.domElement);


	// // OVERLAY TEXT
	// overlayText = document.getElementById('overlay-text');

	// LIGHT
	// can't see textures without light
	var light = new THREE.PointLight(0xffffff);
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


	document.body.addEventListener( 'keydown', function(e) {
	// debug event
	if (e.key === 't')
		SendEvent('debug_print', userName)
	if (e.key === "ArrowUp" || e.key === "ArrowDown")
		e.preventDefault();
	var key = e.code.replace('Key', '').toLowerCase();
	// console.log("key: " + key);
	if ( keys[ key ] !== undefined )
		keys[ key ] = true;
	});

	document.body.addEventListener( 'keyup', function(e) {
	var key = e.code.replace('Key', '').toLowerCase();
	if ( keys[ key ] !== undefined )
		keys[ key ] = false;
	});


	// MATERIAL
	const lineMaterial = new THREE.LineDashedMaterial( { color: 0x353535, linewidth: 1, scale: 1, dashSize: 0.5, gapSize: 0.5 } );
	const paddleMaterial = new THREE.MeshBasicMaterial({ color: 0x353535 });
	const whiteMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
	const blackMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
	const redWireframeMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });
	const paddleOutlineMaterial = new THREE.MeshBasicMaterial({ color: 0xd1d1d1, side: THREE.BackSide });
	const ballMaterial = new THREE.MeshBasicMaterial({map: ballTexture});


	// CUSTOM GEOMETRY

	// Arena
	const arenaFloorGeometry = new THREE.BoxGeometry(16, 9, 0.5);
	const arenaSmallSideGeometry = new THREE.BoxGeometry(0.5, 10, 0.5);
	const arenaLargeSideGeometry = new THREE.BoxGeometry(17, 0.5, 0.5);
	const arenaFloor = new THREE.Mesh(arenaFloorGeometry, blackMaterial);
	const arenaLeftSide = new THREE.Mesh(arenaSmallSideGeometry, whiteMaterial);
	const arenaTopSide = new THREE.Mesh(arenaLargeSideGeometry, whiteMaterial);
	const arenaBottomSide = arenaTopSide.clone();
	const arenaRightSide = arenaLeftSide.clone();
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
	scene.add(ball);


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


function Loop()
{
	if (running == false)
	{
		console.log("Not running anymore!");
		return;
	}
	requestAnimationFrame(Loop);
	Inputs();
	Update();
	renderer.render(scene, camera);
}

function Inputs()
{
	const inputEvent = 'pong_input'
	// Info
	if (keys.i)
	{
		console.log("[INFO]");
		console.log("[right paddle] x: " + leftPaddle.position.x + " y: " + leftPaddle.position.y + " z: " + leftPaddle.position.z);
		console.log("[ball] x: " + ball.position.x + " y: " + ball.position.y + " z: " + ball.position.z);
		console.log("[right paddle] x: " + rightPaddle.position.x + " y: " + rightPaddle.position.y + " z: " + rightPaddle.position.z);
	}

	//CLIENT SIDE PADDLE INPUTS
	if (keys.w)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'up'
		}))
	}

	if (keys.s)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'down'
		}))
	}

	if (keys.arrowup)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'up'
		}))
	}

	if (keys.arrowdown)
	{
		socket.emit(inputEvent, JSON.stringify({
			'username': userName,
			'action':'down'
		}))
	}
}

function Update()
{
	// Paddle Outline
	leftPaddleOutLine.position.y = leftPaddle.position.y;
	rightPaddleOutLine.position.y = rightPaddle.position.y;
}
