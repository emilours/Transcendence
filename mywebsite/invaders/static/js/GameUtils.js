export function createElement(type, properties = {}, ...children) {
	const element = document.createElement(type);
	Object.assign(element, properties);
	children.forEach(child => element.appendChild(child));
	return element;
}

export function createButton(text, onClick) {
	return createElement('button', { innerText: text, className: 'button', onclick: onClick });
}

export function createArrowButton(text, onClick) {
	return createElement('h3', { innerText: text, className: 'arrow', onclick: onClick });
}

export function createButtonGreen(text, onClick) {
	return createElement('button', { innerText: text, className: 'button green', onclick: onClick });
}

export function createPlayerContainer(index, color, playerList) {
	const playerText = createElement('p', { innerText: `Player ${index}`, style: `color: ${color};` });
	const input = createElement('input', { className: 'input',
		type: 'text',
		placeholder: 'Name',
		style: `border-color: ${color};`,
	});

	input.setAttribute('maxlength', '10');

	playerList.push([`player${index}`, `Player${index}`]);

	input.addEventListener('input', event => {
		if (event.target.value.length > 10) {
			event.target.value = event.target.value.slice(0, 10);
		}
		playerList[index - 1][1] = event.target.value;
	});

	return createElement('div', { className: 'button-horizontal' }, playerText, input);
}

export function appendChildren(parent, ...children) {
	children.forEach(child => parent.appendChild(child));
}

export function backButton(screenToRemove, direction) {
	screenToRemove.remove();
	direction();
}

export function shuffleArray(array) {
	for (let i = array.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[array[i], array[j]] = [array[j], array[i]];
	}
}
