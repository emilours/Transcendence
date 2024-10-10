import Player from './Player.js';
import { createElement, appendChildren, createButton, createButtonGreen } from './GameUtils.js';
import { resetGame, startInvaders } from './invaders.js';
import { Color } from "./Colors.js";
import { createPlayerContainer, shuffleArray } from './GameUtils.js';

export default class Tournament {

	constructor(game, playerList, startGame) {
		this.canvas = game.canvas;
		this.currentRound = [];
		this.nextRound = [];
		this.isOver = false;
		this.index = 0;
		this.nextPlayer1 = null;
		this.nextPlayer2 = null;
		this.round = 1;
		this.startGame = startGame;

		for (let [id, name] of playerList)
			this.currentRound.push(new Player(this.canvas, name, id));
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
				resetGame(this.canvas);
				startInvaders(game.userName);
			}),
		);
		document.querySelector('.invaders-container').appendChild(winnerScreen);
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
				resetGame(this.canvas);
				this.startGame('tournament', this.nextPlayer1, this.nextPlayer2, this);
			})
		);
		document.querySelector('.invaders-container').appendChild(tieScreen);
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
						resetGame(this.canvas);
						startInvaders(game.userName);
					}),
					createButtonGreen('NEXT', () => {
						winnerScreen.remove();
						this.getNextMatch();
						this.playNextMatch();
					})
				)
			);
			document.querySelector('.invaders-container').appendChild(winnerScreen);
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
					this.startGame('tournament', this.nextPlayer1, this.nextPlayer2,
						this);
				})
			);
			tournamentStatusScreen.appendChild(nextMatch);
			document.querySelector('.invaders-container').appendChild(tournamentStatusScreen);
		}
	}
}

export function tournamentSetup(startGame, game) {
	const playerList = new Array();
	const playerListContainer = createElement('div', { className: 'player-list' });

	const tournamentScreen = createElement('div', { className: 'menu' },
		createElement('h2', { innerText: 'Tournament' }),
		createElement('h3', { innerText: 'SELECT A SIZE' }),
		createButton('4 PLAYER', () => setupPlayers(4)),
		createButton('8 PLAYERS', () => setupPlayers(8)),
		playerListContainer,
		createElement('div', { className: 'button-horizontal' },
			createButton('MENU', () => {
				tournamentScreen.remove();
				startInvaders(game.userName);
			}),
			createButtonGreen('CREATE', () => {
				if (playerList.length === 4 || playerList.length === 8) {
					tournamentScreen.style.display = 'none';
					shuffleArray(playerList);
					createTournament(new Tournament(game, playerList, startGame));
				} else {
					alertBox.style.color = 'red';
					setTimeout(() => {
						alertBox.style.color = 'transparent';}, 3000);
				}
			})
		)
	);
	const alertBox = createElement('div', { className: 'p',
		innerText: 'Select a size before continue!',
		style: 'color: transparent; font-size: 0.8em;' });
	tournamentScreen.appendChild(alertBox);
	document.querySelector('.invaders-container').appendChild(tournamentScreen);

	function setupPlayers(num) {
		playerListContainer.innerHTML = '';
		playerList.length = 0;

		for (let i = 1; i <= num; i++) {
			const color = Color[`player${i}`];
			const playerContainer = createPlayerContainer(i, color, playerList);
			playerListContainer.appendChild(playerContainer);
		}
	}

	function createTournament(tournament) {
		tournament.playNextMatch();
	}
}
