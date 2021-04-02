'use strict';

let url = new URL(window.location.href)
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)

ws.onmessage = event => {
    let messages = JSON.parse(event['data'])
	let context = ''
	messages.forEach(message => {
		context += '<div class="border shadow-sm rounded p-3 m-3">'
		context += `<p class="lead fs-4">${message.text}</p>`
		context += `<p class="text-end"><span class="badge bg-secondary">${message.authorName}</span> ${message.createAt}</p>`
		context += '</div>'
	})
	$('#chat').html(context)
	console.log(messages[0])
}

ws.onopen = () => {
    alert("Соединение установлено.");
	ws.send('get_chat')
	setInterval(() => {
		ws.send('get_chat')
	}, 5000)
}
