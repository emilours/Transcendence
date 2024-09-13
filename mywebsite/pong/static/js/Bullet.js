export default class Bullet {
	constructor(canvas, x, y, velocity, color) {
		this.canvas = canvas;
		this.x = x;
		this.y = y;
		this.velocity = velocity;
		this.color = color;

		this.width = 5;
		this.height = 10;
	}

	draw(ctx) {
		this.y -= this.velocity;
		ctx.fillStyle = this.color;
		ctx.fillRect(this.x, this.y, this.width, this.height);
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
