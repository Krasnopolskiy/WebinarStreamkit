let url = new URL(window.location.href)
let parent_url = url.href.replace('/control', '')
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)
let chat_widget, awaiting_widget


let close_widget = () => {
    if (chat_widget !== undefined)
        chat_widget.close()
    if (awaiting_widget !== undefined)
        awaiting_widget.close()
    window.close()
}


let update_setting = (settings) => {
    if (settings.status === 'ACTIVE') {
        $('#stop-btn').css('display', 'none')
        $('#start-btn').css('display', 'start')
    }
    if (settings.status === 'START') {
        $('#stop-btn').css('display', 'none')
        $('#start-btn').css('display', 'block')
    }
    if (settings.status === 'STOP')
        close_widget()
    $('#moderate-switch').prop('checked', settings.premoderation)
}


ws.onmessage = event => {
    let data = JSON.parse(event['data'])
    if (data['event'] === 'update settings')
        update_setting(data['settings'])
    if (data['event'] === 'error')
        console.log(data['message'])
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
