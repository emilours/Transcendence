import Enemy from './Enemy.js';
import MovingDirection from './MovingDirection.js';

export default class EnemyController {
	enemyMap = [
		[3, 3, 3, 3, 3, 3, 3, 3, 3],
		[2, 2, 2, 2, 2, 2, 2, 2, 2],
		[2, 2, 2, 2, 2, 2, 2, 2, 2],
		[1, 1, 1, 1, 1, 1, 1, 1, 1],
		[1, 1, 1, 1, 1, 1, 1, 1, 1],
	];
	enemyRows = [];
	currentDirection = MovingDirection.right;
	xVelocity = 0;
	yVelocity = 0;
	velocity = 1.5;
	moveDownTimerDefault = 40;
	moveDownTimer = this.moveDownTimerDefault;
	fireBulletTimerDefault = 100;
	fireBulletTimer = this.fireBulletTimerDefault;

	constructor(canvas, enemyBulletController, player1, player2, mode) {

		this.canvas = canvas;
		this.enemyBulletController = enemyBulletController;
		this.mode = mode;

		this.player1 = player1;
		if (this.mode === 'versus' || this.mode === 'tournament')
			this.player2 = player2;

		this.gifCanvas = document.createElement('canvas');
		this.gifCtx = this.gifCanvas.getContext('2d');
		this.gifCanvas.width = 40;
		this.gifCanvas.height = 40;
		gifler('../../static/img/destroyed.gif').get((a) => {
			a.animateInCanvas(this.gifCanvas);
		});

		this.enemyDeathSound = new Audio("../../static/sounds/enemy-death.wav");
		this.enemyDeathSound.volume = 0.1;
		this.createEnemies();

		if (this.mode === 'arcade') {
			this.addNewEnemyRow();
		}
		else {
			this.fireBulletTimerDefault = 60;
		}
	}

	draw(ctx) {
		this.decrementMoveDownTimer();
		this.updateVelocityAndDirection();
		this.collisionDetection(ctx);
		this.drawEnemies(ctx);
		this.resetMoveDownTimer();
		this.fireBullet();
		this.showScore(ctx);
	}

	showScore(ctx) {
		ctx.font = "12px 'Press Start 2P'";
		if (this.mode === 'arcade') {
			ctx.fillStyle = "white";
			ctx.fillText("Score " + this.player1.score , 70, 20);
		}
		if (this.mode === 'versus' || this.mode === 'tournament') {
			ctx.fillStyle = this.player1.color;
			ctx.fillText("Score " + this.player1.score , 70, 20);
			ctx.fillStyle = this.player2.color;
			ctx.fillText("Score " + this.player2.score, this.canvas.width - 200, 20);
		}
	}

	collisionDetection(ctx) {
		this.enemyRows.forEach((enemyRow) => {
			enemyRow.forEach((enemy, enemyIndex) => {
				if (this.player1.bulletController.collideWith(enemy)) {
					this.player1.score += enemy.points;
					this.destroyEnemy(enemy, enemyIndex, enemyRow, ctx);
				}
				if (this.mode === 'versus' || this.mode === 'tournament') {
					if (this.player2.bulletController.collideWith(enemy)) {
						this.player2.score += enemy.points;
						this.destroyEnemy(enemy, enemyIndex, enemyRow, ctx);
					}
				}
			});
		});
		this.enemyRows = this.enemyRows.filter((enemyRow) => enemyRow.length > 0);
	}

	destroyEnemy(enemy, enemyIndex, enemyRow, ctx) {
		this.enemyDeathSound.currentTime = 0;
		this.enemyDeathSound.play();
		enemyRow.splice(enemyIndex, 1);

		const drawGIF = () => {
			ctx.drawImage(this.gifCanvas, enemy.x, enemy.y, 40, 40);
		};
		const gifInterval = setInterval(drawGIF, 1000 / 30); // FPS
		setTimeout(() => {
			clearInterval(gifInterval);
		}, 300);
	}

	fireBullet() {
		this.fireBulletTimer--;
		if (this.fireBulletTimer <= 0) {
			this.fireBulletTimer = this.fireBulletTimerDefault;
			const allEnemies = this.enemyRows.flat();
			const enemyIndex = Math.floor(Math.random() * allEnemies.length);
			const enemy = allEnemies[enemyIndex];
			this.enemyBulletController.shoot(enemy.x, enemy.y, -3);
		}
	}

	resetMoveDownTimer() {
		if (this.moveDownTimer <= 0) {
			this.moveDownTimer = this.moveDownTimerDefault;
			if (this.mode === 'arcade') {
				this.velocity += 0.02;
				// console.log('Speed up! velocity = ' + this.velocity.toFixed(2));
				this.addNewEnemyRow();
			}
		}
	}

	decrementMoveDownTimer() {
		if (this.currentDirection === MovingDirection.downLeft ||
			this.currentDirection === MovingDirection.downRight) {
			this.moveDownTimer--;
		}
	}

	updateVelocityAndDirection() {
		let changeDirection = false;

		for(const enemyRow of this.enemyRows){
			if (this.currentDirection === MovingDirection.right) {
				this.xVelocity = this.velocity;
				this.yVelocity = 0;
				const rightMostEnemy = enemyRow[enemyRow.length - 1];
				if(rightMostEnemy.x + rightMostEnemy.width >= this.canvas.width){
					changeDirection = true;
					break;
				}
			} else if (this.currentDirection === MovingDirection.left) {
				this.xVelocity = -this.velocity;
				this.yVelocity = 0;
				const leftMostEnemy = enemyRow[0];
				if (leftMostEnemy.x <= 0) {
					changeDirection = true;
					break;
				}
			}
		}
		if (changeDirection) {
			this.currentDirection = this.currentDirection === MovingDirection.right
				? MovingDirection.downLeft
				: MovingDirection.downRight;
		} else if (this.currentDirection === MovingDirection.downLeft) {
			this.moveDown(MovingDirection.left);
		} else if (this.currentDirection === MovingDirection.downRight) {
			this.moveDown(MovingDirection.right);
		}
	}

	addNewEnemyRow() {
		const newEnemyRow = [];

		this.enemyRows[0].forEach((existingEnemy, enemyIndex) => {
			let reference = existingEnemy.x;
			const enemyNumber = Math.floor(Math.random() * 3) + 1;
			if (enemyNumber > 0) {
				newEnemyRow.push(new Enemy(reference, -64, enemyNumber));
			}
			reference += 64;
		});
		this.enemyRows.unshift(newEnemyRow);
	}



	moveDown(newDirection) {
		this.xVelocity = 0;
		this.yVelocity = this.velocity;
		if (this.moveDownTimer <= 0) {
			this.currentDirection = newDirection;
			return true;
		}
		return false;
	}

	drawEnemies(ctx) {
		this.enemyRows.flat().forEach((enemy) => {
			enemy.move(this.xVelocity, this.yVelocity);
			enemy.draw(ctx);
		});
	}

	createEnemies() {
		this.enemyMap.forEach((row, rowIndex) => {
			this.enemyRows[rowIndex] = [];
			row.forEach((enemyNumber, enemyIndex) => {
				if (enemyNumber > 0) {
					this.enemyRows[rowIndex].push(
						new Enemy(enemyIndex * 64, rowIndex * 64, enemyNumber));
				}
			});
		});
	}

	checkIfEnemiesReachedBottom() {
		return this.enemyRows.flat().some(enemy => enemy.y + enemy.height >= this.canvas.height);
	}

	collideWith(sprite) {
		return this.enemyRows.flat().some(enemy => enemy.collideWith(sprite));
	}
}
