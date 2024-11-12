
function CreateGameHud()
{
	const gameHud = createElement('div', {className: 'game-hud' },
		createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
			createElement('h2', { innerText: ""}),
			createElement('h3', { innerText: "0:0"}),
			createElement('h3', { innerText: ""})
		)
	);
	document.querySelector('.pong-container').appendChild(gameHud);
}


//
function UpdateGameOverlay(gameText, gameOver)
{
	const gameOverlay = document.querySelector('.overlay');
	if (gameOverlay)
	{
		const overlayH2 = gameOverlay.querySelector('h2');
		if (overlayH2)
			overlayH2.innerText = "";

		const overlayH3 = gameOverlay.querySelector('h3');
		if (overlayH3)
			overlayH3.innerText = gameText;

		if (gameOver == 1)
		{
			if (overlayH2)
				overlayH2.innerText = "WINNER";
			let quitButton = gameOverlay.querySelector('button');
			if (!quitButton)
			{
				quitButton = createButton('QUIT', () => {
					gameOverlay.remove();
					Cleanup();
					CloseWebsocket();
					ResetGameCanvas();
					initPongMenu();
				});
			}

			gameOverlay.appendChild(quitButton);
		}

	}
}

function RemoveGameOverlay()
{
	const gameOverlay = document.querySelector('.overlay');
	if (gameOverlay)
	{
		document.querySelector('.pong-container').removeChild(gameOverlay);
		gameOverlay.remove();
	}
}