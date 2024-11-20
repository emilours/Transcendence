import {createElement,  createButton} from './GameUtils.js';
import { CloseWebsocket, Cleanup } from './pong.js';
import { initPongMenu } from './pongMenu.js';


const HUD_IMAGE_SIZE = 75;
const TOURNAMENT_MODE = 'tournament';
const DEFAULT_AVATAR = '/static/img/avatarDefault.gif';
const NORMAL_MODE = 'normal';

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


export function DrawLocalGameHud(scores)
{
    let gameHud;
    gameHud = createElement('div', {className: 'game-hud' },
        createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
            createElement('img', {className: 'rounded-circle', style: 'border: 5px solid green;', src: DEFAULT_AVATAR, width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} ),
            createElement('h3', { innerText: "Player1"}),
            createElement('h3', { innerText: scores[0] + "  :  " + scores[1]}),
            createElement('h3', { innerText: "Player2"}),
            createElement('img', {className: 'rounded-circle', style: 'border: 5px solid green;', src: DEFAULT_AVATAR, width: HUD_IMAGE_SIZE, height: HUD_IMAGE_SIZE} )
        )
    );
	document.querySelector('.pong-container').appendChild(gameHud);
}



export function DrawGameOverlay(mode, text, avatar, userName, winner)
{
    let gameOverlay;
    let h2Text = "WINNER";
    if (mode === 'gameover')
    {

        if (text == "final")
            h2Text = "TOURNAMENT WINNER";
        console.log("h2Text:", h2Text, "text:", text);
        if (winner == userName && text !== "final")
        {
            gameOverlay = createElement('div', {className: 'overlay' },
                createElement('h2', { innerText: h2Text}),
                createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
                    createElement('img', {className: 'rounded-circle', src: avatar, width: 50, height: 50} ),
                    createElement('h3', { innerText: winner})),
                createElement('h4', { innerText: text, style: 'padding-top: 15px;'})
            );
        }
        else
        {
            let quitButton;
            gameOverlay = createElement('div', {className: 'overlay' },
                createElement('h2', { innerText: h2Text}),
                createElement('div', { className: 'button-horizontal', style: 'align-items: flex-start;'},
                    createElement('img', {className: 'rounded-circle', src: avatar, width: 50, height: 50} ),
                    createElement('h3', { innerText: winner})
                    ),
                quitButton = createButton('QUIT', () => {
                    gameOverlay.remove();
                    RemoveMenu('.game-hud');
                    CloseWebsocket();
                    Cleanup();
                    initPongMenu();
                }));
        }
    }
    else if (mode === 'waiting')
    {
        gameOverlay = createElement('div', {className: 'overlay' },
            createElement('h3', { innerText: text}),
        );
    }
    document.querySelector('.pong-container').appendChild(gameOverlay);
}

export function RemoveMenu(className)
{
	const menu = document.querySelector(className);
	if (menu)
	{
		document.querySelector('.pong-container').removeChild(menu);
		menu.remove();
	}
}
