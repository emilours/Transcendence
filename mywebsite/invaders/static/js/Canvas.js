import EnemyController from './EnemyController.js';
import BulletController from './BulletController.js';

export default class Canvas {
	constructor(userName) {
		// Config canvas
		this.canvas = document.getElementById('game');
		if (!this.canvas) {
			this.canvas = document.createElement('canvas');
			this.canvas.id = 'game';
			document.body.appendChild(this.canvas);
		}
		this.ctx = this.canvas.getContext('2d');
		this.gameInterval = null;
		this.canvas.width = 700;
		this.canvas.height = 700;

		// Gif background
		this.gifCanvas = document.createElement('canvas');
		this.gifCanvas.width = this.canvas.width;
		this.gifCanvas.height = this.canvas.height;
		this.gifAnimation = gifler("../../static/img/background.gif").get((a) => {
			a.animateInCanvas(this.gifCanvas);
		});

		this.enemyController = new EnemyController(this.canvas);
		this.enemyBulletController = new BulletController(this.canvas);
		this.isGameOver = false;
		this.didWin = false;
		this.userName = userName;
	}
}