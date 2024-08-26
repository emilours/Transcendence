import BulletController from "./BulletController.js";
import { Color } from "./Colors.js";

export default class Player {
	rightPressed = false;
	leftPressed = false;
	shootPressed = false;

	constructor(canvas, name, id) {
		this.canvas = canvas;
		this.name = name;
		this.id = id;
		this.color = Color[id];
		this.control = 1;
		this.velocity = 6;
		this.score = 0;
		this.isDestroyed = false;
		this.isFinished = false;
		this.x = this.canvas.width / 2;
		this.y = this.canvas.height - 100;
		this.width = 62;
		this.height = 70;
		this.image = new Image();
		this.image.src = `../../static/img/${id}.png`;

		this.gifCanvas = document.createElement('canvas');
		this.gifCtx = this.gifCanvas.getContext('2d');
		this.gifCanvas.width = this.width;
		this.gifCanvas.height = this.height;
		gifler('../../static/img/destroyed.gif').get((a) => {
			a.animateInCanvas(this.gifCanvas);
		});

		this.bulletController = new BulletController(canvas, 5, this.color, true);
		this.leftKey = "KeyA";
		this.rightKey = "KeyD";
		this.shootKey = "KeyW";

		document.addEventListener("keydown", this.keydown);
		document.addEventListener("keyup", this.keyup);
	}

	draw(ctx) {
		if (this.isDestroyed && this.isFinished === false) {
			ctx.drawImage(this.gifCanvas, this.x, this.y, this.width, this.height);
			setTimeout(() => {
				this.isFinished = true;
			}, 1000);
			return;
		} else if (this.isFinished)
			return;
		if (this.shootPressed) {
			this.bulletController.shoot(this.x + this.width / 2, this.y, 4, 10);
		}
		this.move();
		this.collideWithWalls();
		ctx.drawImage(this.image, this.x, this.y, this.width, this.height);
	}

	setClassicControls() {
		this.control = 1;
		this.leftKey = "KeyA";
		this.rightKey = "KeyD";
		this.shootKey = "KeyW";
	}

	setAltControls() {
		this.control = 2;
		this.leftKey = "ArrowLeft";
		this.rightKey = "ArrowRight";
		this.shootKey = "ArrowUp";
	}

	collideWithWalls() {
		if (this.x < 0)
			this.x = 0;
		if (this.x > this.canvas.width - this.width)
			this.x = this.canvas.width - this.width;
	}

	move() {
		if (this.rightPressed)
			this.x += this.velocity;
		else if (this.leftPressed)
			this.x += -this.velocity;
	}

	keydown = (event) => {
		if (event.code == this.rightKey)
			this.rightPressed = true;
		if (event.code == this.leftKey)
			this.leftPressed = true;
		if (event.code == this.shootKey)
			this.shootPressed = true;
	};

	keyup = (event) => {
		if (event.code == this.rightKey)
			this.rightPressed = false;
		if (event.code == this.leftKey)
			this.leftPressed = false;
		if (event.code == this.shootKey)
			this.shootPressed = false;
	};

	reset() {
		this.isDestroyed = false;
		this.isFinished = false;
		this.score = 0;
		this.bulletController.clearBullets();
	}

	updateId(id) {
		this.id = `player${id}`;
		this.color = Color[`player${id}`];
		this.image.src = `../../static/img/player${id}.png`;
		this.bulletController.bulletColor = Color[`player${id}`];
	}
}
