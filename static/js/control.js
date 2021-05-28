let url = new URL(window.location.href)
let parent_url = url.href.replace('/control', '')
let ws_protocol = url.protocol === 'http:' ? 'ws:' : 'wss:'
let ws = new WebSocket(`${ws_protocol}//${url.host}${url.pathname}`)
let chat_widget, awaiting_widget

let close_widget = () => {
    if (chat_widget !== undefined)
        chat_widget.close()
    if (awaiting_widget !== undefined)
        awaiting_widget.close()
    window.close()
}

let update_fontsize = () => {
    let fontsize = parseInt($('#fontsize-range').val())
    $('#fontsize-value').html(fontsize)
    if (chat_widget !== undefined) {
        $('.display-6', chat_widget.document).css('font-size', `${fontsize + 12}px`)
        $('#message-box', chat_widget.document).css('font-size', `${fontsize}px`)
    }
    if (awaiting_widget !== undefined) {
        $('.display-6', awaiting_widget.document).css('font-size', `${fontsize + 12}px`)
        $('#message-box', awaiting_widget.document).css('font-size', `${fontsize}px`)
    }
}

let update_setting = (settings) => {
    if (settings.status === 'ACTIVE') {
        $('#stop-btn').css('display', 'none')
        $('#start-btn').css('display', 'block')
    }
    if (settings.status === 'START') {
        $('#stop-btn').css('display', 'block')
        $('#start-btn').css('display', 'none')
    }
    if (settings.status === 'STOP')
        close_widget()
    $('#moderate-switch').prop('checked', settings.premoderation)
}

ws.onmessage = event => {
    data = JSON.parse(event['data'])
    if (data['event'] === 'update settings')
        update_setting(data['settings'])
    if (data['event'] === 'error')
        console.log('WS error')
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
    iziToast.warning({
        message: 'Изменения вступят в силу через некоторое время'
    })
})


$('#fontsize-range').on('change', () => {
    let payload = {
        command: 'update fontsize',
        params: {
            fontsize: $('#fontsize-range').val()
        }
    }
    ws.send(JSON.stringify(payload))
    update_fontsize()
})

$('#start-btn').click(() => {
    let payload = {
        command: 'start',
        params: {}
    }
    ws.send(JSON.stringify(payload))
    // location.reload()
})

$('#stop-btn').click(() => {
    let payload = {
        command: 'stop',
        params: {}
    }
    ws.send(JSON.stringify(payload))
    // location.reload()
})

$('#chat-btn').click(() => {
    if (chat_widget === undefined || chat_widget.closed)
        chat_widget = window.open(`${parent_url}/chat`, 'Chat', `height=${100*vh * 2}, width=${100*vw}, left=${100*vw + 10}`)
    setTimeout(() => update_fontsize(), 1000)
})

$('#awaiting-btn').click(() => {
    if (awaiting_widget === undefined || awaiting_widget.closed)
        awaiting_widget = window.open(`${parent_url}/awaiting`, 'Awaiting', `height=${100*vh * 2}, width=${100*vw}, left=${(100*vw + 10) * 2}`)
    setTimeout(() => update_fontsize(), 1000)
})
