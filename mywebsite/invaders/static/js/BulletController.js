import Bullet from "./Bullet.js";

export default class BulletController {
	bullets = []
	timeTillNextBulletAllowed = 0;

	constructor (canvas, maxBulletAtTime, bulletColor, sounfEnabled) {
		this.canvas = canvas;
		this.maxBulletAtTime = maxBulletAtTime;
		this.bulletColor = bulletColor;
		this.soundEnabled = sounfEnabled;

		this.shootSound = new Audio("../../static/sounds/shoot.wav");
		this.shootSound.volume = 0.3;
	}

	draw(ctx) {
		this.bullets = this.bullets.filter(bullet => bullet.y + bullet.width > 0
			&& bullet.y <= this.canvas.height);

		this.bullets.forEach(bullet => bullet.draw(ctx));
		if (this.timeTillNextBulletAllowed > 0) {
			this.timeTillNextBulletAllowed--;
		}
	}

	collideWith(sprite) {
		const bulletThatSpriteIndex = this.bullets.findIndex(bullet =>
			bullet.collideWith(sprite)
		);
		if (bulletThatSpriteIndex >= 0) {
			this.bullets.splice(bulletThatSpriteIndex, 1);
			return true;
		}
		return false;
	}

	shoot(x, y, velocity, timeTillNextBulletAllowed = 0) {
		if (this.timeTillNextBulletAllowed <= 0 &&
			this.bullets.length < this.maxBulletAtTime) {
			const bullet = new Bullet(this.canvas, x, y, velocity, this.bulletColor);
			this.bullets.push(bullet);
			if (this.soundEnabled) {
				this.shootSound.currentTime = 0;
				this.shootSound.play();
			}
			this.timeTillNextBulletAllowed = timeTillNextBulletAllowed;
		}
	}

	clearBullets() {
		this.bullets = [];
		this.timeTillNextBulletAllowed = 0;
	}
}
