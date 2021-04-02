'use strict';

let url = new URL(window.location.href)
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)

let update_chat = template => {
    if (template !== $('#chat').html()) {
        $('#chat').html(template)
        update_event_handlers()
    }
}

let update_event_handlers = () => {
    $('.delete-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        console.log(`Deleting <Message ${message_id}> ...`)
    })

    $('.accept-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        ws.send(`{"command": "accept message", "message_id": ${message_id}}`)
    })

    $('.decline-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        console.log(`Declining <Message ${message_id}> ...`)
    })
}
let last_scroll_pos_moder = 0;
let last_scroll_pos_await = 0;
ws.onmessage = event => {
    let data = JSON.parse(event['data'])
    if (data['event'] == 'update chat') {
        update_chat(data['template']);
        document.querySelector('#moderated').scrollTop = last_scroll_pos_moder;
        document.querySelector('#awaiting').scrollTop = last_scroll_pos_await;
    }
    $('#moderated').on("scroll", function(event) {
        last_scroll_pos_moder = $('#moderated').scrollTop();
    });
    $('#awaiting').on("scroll", function(event) {
        last_scroll_pos_await = $('#awaiting').scrollTop();
    });
}

