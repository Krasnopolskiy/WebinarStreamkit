let last_scroll_pos = 0
let url = new URL(window.location.href)
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)

let update_messages = template => {
    if (template !== $('#message-box').html()) {
        $('#message-box').html(template)
        update_event_handlers()
    }
}

let update_event_handlers = () => {
    $('.accept-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        ws.send(`{"command": "accept message", "message_id": ${message_id}}`)
    })

    $('.delete-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        ws.send(`{"command": "delete message", "message_id": ${message_id}}`)
    })
}

ws.onmessage = event => {
    let data = JSON.parse(event['data'])

    if (data['event'] == 'update messages') {
        update_messages(data['template'])
        document.querySelector('#message-box').scrollTop = last_scroll_pos
    }

    $('#message-box').on('scroll', function (event) {
        last_scroll_pos = $('#message-box').scrollTop()
    })
}
