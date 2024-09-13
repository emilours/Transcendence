export default class Enemy {
	constructor(x, y, imageNumber) {
		this.x = x;
		this.y = y;
		this.width = 54;
		this.height = 54;
		this.points = imageNumber * 10;
		this.isDestroyed = false;
		this.isFinished = false;

		this.image = new Image();
		this.image.src = `../../static/img/enemy${imageNumber}.png`;
	}

	draw(ctx) {
		ctx.drawImage(this.image, this.x, this.y, this.width, this.height);
	}

	move(xVelocity, yVelocity) {
		this.x += xVelocity;
		this.y += yVelocity;
	}

	collideWith(sprite) {
		if (this.x + this.width > sprite.x &&
			this.x < sprite.x + sprite.width &&
			this.y + this.height > sprite.y &&
			this.y < sprite.y + sprite.height) {
			return true;
		}
		return false;
	}
}

