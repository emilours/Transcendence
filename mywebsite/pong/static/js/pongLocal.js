import * as THREE from './three.module.js';
import { TextGeometry } from './TextGeometry.js';
import { FontLoader } from './FontLoader.js';


// standard global variables
var scene, camera, renderer, loader;

// THREEJS object variables
var line, ball, ballBB, ballTexture, leftPaddle, leftPaddleOutLine, leftPaddleBB, rightPaddle, rightPaddleOutLine, rightPaddleBB, keys, scoreMesh;


var overlayText;
var scoreGeometry, scoreFont, gameOver;
const PADDLE_SPEED = 8.0;
const PADDLE_WIDTH = 0.2;
const BALL_SPEED = 2.0;
const BALL_SIZE = 0.2; // maybe a bit bigger
const MAX_HEIGHT = 4.5;
const MIN_HEIGHT = -4.5;
var ballSpeed = {x: BALL_SPEED, y: BALL_SPEED};
var leftPlayerScore = 0; // player 1
var rightPlayerScore = 0; // player 2
var running = true;
var lastTime = 0;
var deltaTime = 0;


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

export function CleanupLocalPong()
{
	running = false;
}

export function StartLocalGame()
{
	Load();
	Init();
	requestAnimationFrame(Loop);
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
	ballTexture = textureLoader.load("../../static/textures/ballTextureOrange.png")

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
	// reset values
	running = true;
	leftPlayerScore = 0;
	rightPlayerScore = 0;
	lastTime = 0;
	deltaTime = 0;
	ballSpeed = {x: BALL_SPEED, y: BALL_SPEED};

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
	if (overlayText.classList.contains('menu'))
	{
		overlayText.classList.remove('menu');
		overlayText.classList.add('text-overlay');
		overlayText.textContent = ``;
	} 

	// LIGHTS
	// can't see textures without light
	var light = new THREE.PointLight(0xffffff);
	light.position.set(0, 0, 10);
	scene.add(light);

	// INPUTS
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


	// MATERIALS
	const lineMaterial = new THREE.LineDashedMaterial( { color: 0x353535, linewidth: 1, scale: 1, dashSize: 0.5, gapSize: 0.5 } );
	const paddleMaterial = new THREE.MeshBasicMaterial({ color: 0x353535 });
	const whiteMaterial = new THREE.MeshBasicMaterial({ color: 0xffffff });
	const blackMaterial = new THREE.MeshBasicMaterial({ color: 0x000000 });
	const redWireframeMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000, wireframe: true });
	const paddleOutlineMaterial = new THREE.MeshBasicMaterial({ color: 0xd1d1d1, side: THREE.BackSide });
	const ballMaterial = new THREE.MeshBasicMaterial({map: ballTexture});


	// CUSTOM GEOMETRY

	// ARENA
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

	// BALL
	// const cubeGeometry = new THREE.BoxGeometry(0.4, 0.4, 0.4);
	const ballGeometry = new THREE.SphereGeometry(BALL_SIZE, 64, 32);
	// cube = new THREE.Mesh(cubeGeometry, redWireframeMaterial);
	ball = new THREE.Mesh(ballGeometry, ballMaterial);
	// scene.add(cube);
	ball.position.x = 0;
	ball.position.y = 0;
	scene.add(ball);

	ballBB = new THREE.Sphere(ball.position, BALL_SIZE);



	// PADDLES
	const paddleGeometry = new THREE.BoxGeometry(PADDLE_WIDTH, 2, 0.2);
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


	// MIDDLE LINE
	const points = [];
	points.push( new THREE.Vector3( 0, MAX_HEIGHT, -0.20 ) );
	points.push( new THREE.Vector3( 0, MIN_HEIGHT, -0.20) );
	const lineGeometry = new THREE.BufferGeometry().setFromPoints( points );
	line = new THREE.Line( lineGeometry, lineMaterial );
	scene.add(line);
	line.computeLineDistances();

}


function Loop(timestamp)
{
	if (lastTime == 0)
		lastTime = timestamp;
	if (running == false)
	{
		console.log("Not running anymore!");
		return;
	}
	// requestAnimationFrame(Loop);
	Inputs();
	Update(timestamp);
	renderer.render(scene, camera);
	requestAnimationFrame(Loop);
}

function Inputs()
{
	// DISABLE INPUT IF GAME NOT RUNNING
	if (running == false)
		return;

	// DEBUG INFO
	if (keys.i)
	{
		console.log("[INFO]");
		console.log("[right paddle] x: " + leftPaddle.position.x + " y: " + leftPaddle.position.y + " z: " + leftPaddle.position.z);
		console.log("[ball] x: " + ball.position.x + " y: " + ball.position.y + " z: " + ball.position.z);
		console.log("[right paddle] x: " + rightPaddle.position.x + " y: " + rightPaddle.position.y + " z: " + rightPaddle.position.z);
	}

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

function Update(timestamp)
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
		createScoreText();
		ball.position.x = 0;
		ball.position.y = 0;
	}
	if (ball.position.x + BALL_SIZE >= 8)
	{
		leftPlayerScore += 1;
		createScoreText();
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
		if (overlayText.classList.contains('text-overlay'))
		{
			overlayText.classList.remove('text-overlay');
			overlayText.classList.add('menu');
			overlayText.textContent = `GAME OVER`;
		}

		// SaveMatch();

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
	.then(data => {
		if (data.status === 'success') {
			console.log("Pong score save to database successfully!");
		}
		else {
			console.error('Error saving score:', data.message);
		}
	})
	.catch(error => {
		console.error('Error: ', error);
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


