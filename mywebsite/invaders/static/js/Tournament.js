import Player from './Player.js';
import { createElement, appendChildren, createButton, createButtonGreen } from './GameUtils.js';
import { resetGame, drawMenu, startGame } from './invaders.js';

export default class Tournament {

	constructor(canvas, playerList) {
		this.canvas = canvas;
		this.currentRound = [];
		this.nextRound = [];
		this.isOver = false;
		this.index = 0;
		this.nextPlayer1 = null;
		this.nextPlayer2 = null;
		this.round = 1;

		for (let [id, name] of playerList)
			this.currentRound.push(new Player(canvas, name, id));
		this.updateNextPlayers();
	}

	updateNextPlayers() {
		if (this.nextPlayer1 && this.nextPlayer2) {
			this.nextPlayer1.reset();
			this.nextPlayer2.reset();
		}
		if (this.index < this.currentRound.length) {
			this.nextPlayer1 = this.currentRound[this.index++];
			this.nextPlayer1.setClassicControls();
			this.nextPlayer2 = this.currentRound[this.index++];
			this.nextPlayer2.setAltControls();
		}
	}

	getNextMatch() {
		if (this.index >= this.currentRound.length) {
			if (this.nextRound.length === 1) {
				this.isOver = true;
				return this.showTournamentWinner();
			}
			this.currentRound = this.nextRound;
			this.nextRound = [];
			this.round++;
			this.index = 0;
		}
		this.updateNextPlayers();
	}

	showTournamentWinner() {
		const winnerScreen = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'TOURNAMENT WINNER' }),
			createElement('h3', { innerText: 'Congratulations!' }),
			createElement('h3', { innerText: this.nextRound[0].name,
				style: `color: ${this.nextRound[0].color}; margin-bottom: 20px;` }),
			createButton('MENU', () => {
				winnerScreen.remove();
				resetGame();
				drawMenu();
			}),
		);
		document.body.appendChild(winnerScreen);
	}

	showRoundMatches() {
		const playerArray = Array.from(this.currentRound);

		const list = createElement('div', { className: 'button-vertical' });
		for (let i = 0; i < playerArray.length; i++) {
			const matchText = createElement('div', { className: 'button-horizontal' });
			const player1Name = createElement('h3', { innerText: playerArray[i].name, style: `color: ${playerArray[i].color};` });
			const vsText = createElement('h3', { innerText: '  vs  ' });
			const player2Name = createElement('h3', { innerText: playerArray[i + 1].name, style: `color: ${playerArray[i + 1].color};` });

			appendChildren(matchText, player1Name, vsText, player2Name);
			list.appendChild(matchText);
			i++;
		}
		return list;
	}

	tieMatch() {
		const tieScreen = createElement('div', { className: 'menu' },
			createElement('h2', { innerText: 'TIE MATCH' }),
			createElement('h3', { innerText: 'No winner' }),
			createButton('PLAY AGAIN', () => {
				tieScreen.remove();
				this.nextPlayer1.reset();
				this.nextPlayer2.reset();
				resetGame();
				startGame('tournament', this.nextPlayer1, this.nextPlayer2, this);
			})
		);
		document.body.appendChild(tieScreen);
	}

	onMatchEnd(player1, player2) {
		if (player1.score === player2.score) {
			this.tieMatch();
			return;
		}

		let winner;
		if (player1.score > player2.score)
		{
			winner = player1;
			player2.name = '---';
		} else {
			winner = player2;
			player1.name = '---';
		}
		this.nextRound.push(winner);

		if (this.currentRound.length === 0 && this.nextRound.length === 1)
			this.isOver = true;

		if (winner) {
			const winnerScreen = createElement('div', { className: 'menu' },
				createElement('h2', { innerText: 'THE WINNER' }),
				createElement('h3', { innerText: winner.name, style: `color: ${winner.color};` }),
				createElement('p', { innerText: `SCORE ${winner.score}`, style: 'margin-bottom: 20px;' }),
				createElement('div', { className: 'button-horizontal' },
					createButton('MENU', () => {
						winnerScreen.remove();
						resetGame();
						drawMenu();
					}),
					createButtonGreen('NEXT', () => {
						winnerScreen.remove();
						this.getNextMatch();
						this.playNextMatch();
					})
				)
			);
			document.body.appendChild(winnerScreen);
		}
	}

	playNextMatch() {
		if (this.isOver) return;
		const tournamentStatusScreen = createElement('div', { className: 'menu' });
		const controlsText = createElement('h2', { innerText: 'TOURNAMENT' });
		const roundNumberText = createElement('h3', { innerText: `ROUND ${this.round}` });
		appendChildren(tournamentStatusScreen, controlsText, roundNumberText);

		const roundMatches = this.showRoundMatches();
		tournamentStatusScreen.appendChild(roundMatches);

		if (this.nextPlayer1 && this.nextPlayer2) {
			const nextMatch = createElement('div', { className: 'button-vertical' },
				createElement('h3', { innerText: 'NEXT MATCH',
					style: 'margin-top: 70px; color: #ffce08;' }),
				createElement('div', { className: 'button-horizontal' },
					createElement('h3', { innerText: this.nextPlayer1.name,
						style: `color: ${this.nextPlayer1.color};` }),
					createElement('h3', { innerText: '  vs  ' }),
					createElement('h3', { innerText: this.nextPlayer2.name,
						style: `color: ${this.nextPlayer2.color};` })
				),
				createButtonGreen('START MATCH', () => {
					tournamentStatusScreen.remove();
					startGame('tournament', this.nextPlayer1, this.nextPlayer2,
						this);
				})
			);
			tournamentStatusScreen.appendChild(nextMatch);
			document.body.appendChild(tournamentStatusScreen);
		}
	}
}
