import * as THREE from './three.module.js';
// import { OrbitControls } from './OrbitControls.js';
import { TextGeometry } from './TextGeometry.js';
import { FontLoader } from './FontLoader.js';


// standard global variables
var scene, camera, renderer, controls, loader;

// custom global variables
var line, ball, ballBB, ballTexture, leftPaddle, leftPaddleOutLine, leftPaddleBB, rightPaddle, rightPaddleOutLine, rightPaddleBB, keys, scoreMesh;
var overlayText;
// TODO: when connecting (if thread created on server) get thread id and stop thread when disconnecting
// OR just on thread starts a launch of server and handles everything -> connection, disconnection ...
// var threadID;
var gameType, socket;
var userName, user1, user2;
var scoreGeometry, scoreFont, gameOver;
// const PADDLE_SPEED = 0.2;
const BALL_SPEED = 0.1;
const BALL_SIZE = 0.2; // maybe a bit bigger
const MAX_HEIGHT = 4.5; // idk how to name this
const MIN_HEIGHT = -4.5;
var ballSpeed = {x: BALL_SPEED, y: BALL_SPEED};
var leftPlayerScore = 0; // player 1
var rightPlayerScore = 0; // player 2
var running = true;
var menu, player1Info, player2Info;

export function UpdateWaitingPlayer(player1, player2)
{
	// /!\ Those 2 lines are very different:
	// console.log("player1: ", player1);
	// console.log("player1: " + player1);
	// /!\
	player1Info = player1;
	player2Info = player2;
	// modify user
}

export function GetUsers()
{
	const user_1 = { name: user1 };
	const user_2 = { name: user2 };
	return [user1, user2];
}

// FUNCTIONS TO TIGGER EVENT ON SOCKET.IO SERVER
export function SendEvent(event, lobbyMenu)
{
	console.log("SendEvent()");
	menu = lobbyMenu;
	console.log("menu: ", menu);

	if (!socket || !socket.connected)
	{
		console.log("Socket.io connection not open");
		return false;
	}
	socket.emit(event);
	return true;
}

export function ConnectWebsocket(type, username)
{
	// WEBSOCKET
	running = true;
	gameType = type;
	userName = username;
	console.log("Connecting to game: " + gameType + " for user: " + username);

	if (socket && socket.connected) {
        socket.disconnect();  // Disconnect the existing socket
        console.log('Existing socket disconnected');
    }
	
	socket = io("http://localhost:6789", {
		transportOptions: {
			polling: {
				extraHeaders: {
					'X-Username': username,
					'X-Gametype': gameType
				}
			}
		}
	});


	socket.on("connect", function() {
		console.log("Connected to the server");
	});
	socket.on("message", function(message) {
		console.log("Message from server: ", message);
	});

	// DISCONNECT/ERROR EVENTS
	socket.on("disconnect", function(reason) {
		console.log("Disconnected from the server due to: " + reason);
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
		console.log("There is " + count + " client connected");
	});
	socket.on('user_joined', function(user) {
		console.log("User " + user + " has joined.");
	});
	socket.on('user_left', function(user) {
		console.log("User " + user + " has left.");
	});
	socket.on('game_ready', function() {
		console.log("BOTH PLAYER READY");
		menu.remove();
		StartGame();
		SendEvent('start_game', menu);
	});
	// might not be needed anymore
	// socket.on('init_game', function() {
	// 	console.log("init_game event called!");
	// 	menu.remove();
	// 	StartGame();
	// });
	socket.on('send_users', function(data) {
		console.log("Users received: user1 - " + data[0] + " | user2 - " + data[1]);
		user1 = data[0];
		user2 = data[1];

		if (player1Info)
		{
			console.log("updating player1info");
			const playerUsername = player1Info.querySelector('h4');
			if (playerUsername) {
				playerUsername.innerText = user1;
			}
			const playerImage = player1Info.querySelector('img');
			if (playerImage) {
				playerImage.src = '/static/img/avatarDefault.gif';
				playerImage.width = 200;
				playerImage.height = 200;
				playerImage.removeAttribute('style');
			}
		}

		if (player2Info)
		{
			console.log("updating player2info");
			const playerUsername = player2Info.querySelector('h4');
			if (playerUsername) {
				playerUsername.innerText = user2;
			}
			const playerImage = player2Info.querySelector('img');
			if (playerImage) {
				playerImage.src = '/static/img/avatarDefault.gif';
				playerImage.width = 200;
				playerImage.height = 200;
				playerImage.removeAttribute('style');
			}
		}
	});
}

export function CloseWebsocket() {
	if (socket && socket.connected) {
		socket.disconnect();
		console.log("Socket.IO connection closed");
	}
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
			ballSpeed.x = parseFloat(data.ballVelocity[0]);
			ballSpeed.y = parseFloat(data.ballVelocity[1]);
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


	// OVERLAY TEXT
	overlayText = document.getElementById('overlay-text');

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
