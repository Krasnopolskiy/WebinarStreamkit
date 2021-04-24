let url = new URL(window.location.href)
let parent_url = url.href.replace('/control', '')
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)
let chat_widget, awaiting_widget

ws.onmessage = event => {
    let data = JSON.parse(event['data'])
    console.log(data)
}

$('#moderate-switch').on('change', () => {
    let payload = {
        command: 'update settings',
        params: {
            option: 'premoderation',
            value: $('#moderate-switch').is(':checked')
        }
    }
    ws.send(JSON.stringify(payload))
})

$('#start-btn').click(() => {
    let payload = {
        command: 'start',
        params: {}
    }
    ws.send(JSON.stringify(payload))
    location.reload()
})

$('#stop-btn').click(() => {
    let payload = {
        command: 'stop',
        params: {}
    }
    ws.send(JSON.stringify(payload))
    location.reload()
})

$('#chat-btn').click(() => {
    if (chat_widget === undefined || chat_widget.closed)
        chat_widget = window.open(`${parent_url}/chat`, 'Chat', `height=${100*vh * 2}, width=${100*vw}, left=${100*vw + 10}`)
})

$('#awaiting-btn').click(() => {
    if (awaiting_widget === undefined || awaiting_widget.closed)
        awaiting_widget = window.open(`${parent_url}/awaiting`, 'Awaiting', `height=${100*vh * 2}, width=${100*vw}, left=${(100*vw + 10) * 2}`)
})
