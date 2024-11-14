import {createElement,  createButton} from './GameUtils.js';
import { CloseWebsocket } from './pong.js';

const HUD_IMAGE_SIZE = 75;

export function DrawGameHud(userName, usernames, avatars, scores)
{
    let gameHud;
    if (userName == usernames[0])
    {
        gameHud = createElement('div', {className: 'game-hud' },
            createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
                createElement('img', {className: 'rounded-circle', style: 'border: 5px solid green;',src: avatars[0], width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} ),
                createElement('h3', { innerText: usernames[0]}),
                createElement('h3', { innerText: scores[0] + "  :  " + scores[1]}),
                createElement('h3', { innerText: usernames[1]}),
                createElement('img', {className: 'rounded-circle', src: avatars[1], width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} )
            )
        );
    }
    else
    {
        gameHud = createElement('div', {className: 'game-hud' },
            createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
                createElement('img', {className: 'rounded-circle', src: avatars[0], width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} ),
                createElement('h3', { innerText: usernames[0]}),
                createElement('h3', { innerText: scores[0] + "  :  " + scores[1]}),
                createElement('h3', { innerText: usernames[1]}),
                createElement('img', {className: 'rounded-circle', style: 'border: 5px solid green;', src: avatars[1], width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} )
            )
        );
    }
	document.querySelector('.pong-container').appendChild(gameHud);
}

export function RemoveGameHud()
{
	const gameOverlay = document.querySelector('.game-hud');
	if (gameOverlay)
	{
		document.querySelector('.pong-container').removeChild(gameOverlay);
		gameOverlay.remove();
	}
}

export function DrawGameOverlay(mode, text, avatar)
{
    let gameOverlay;
    if (mode === 'gameover')
    {
        let quitButton;
        gameOverlay = createElement('div', {className: 'overlay' },
            createElement('h2', { innerText: "WINNER"}),
            createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
                createElement('img', {className: 'rounded-circle', src: avatar, width: 50, height: 50} ),
                createElement('h3', { innerText: text})
                ),
            quitButton = createButton('QUIT', () => {
                gameOverlay.remove();
                RemoveGameHud();
                CloseWebsocket();
                while (scene.children.length > 0) {
                    scene.remove(scene.children[0]);
                    }
                renderer.render(scene, camera);
                renderer.clear(true, true, true);
                renderer.setSize(0, 0);
                renderer.setSize(window.innerWidth, window.innerHeight);
                initPongMenu();
            }));
    }
    else if (mode === 'waiting')
    {
        gameOverlay = createElement('div', {className: 'overlay' },
            createElement('h3', { innerText: text}),
        );
    }
    document.querySelector('.pong-container').appendChild(gameOverlay);
}

export function RemoveGameOverlay()
{
	const gameOverlay = document.querySelector('.overlay');
	if (gameOverlay)
	{
		document.querySelector('.pong-container').removeChild(gameOverlay);
		gameOverlay.remove();
	}
}
