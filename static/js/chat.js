'use strict';


let url = new URL(window.location.href)
let ws = new WebSocket(`ws://${url.host}${url.pathname}`)

let make_message_template = message => {
    // Security alert: must sanitize message fields because of the xss threat
    let context = String()
    context += '<div class="rounded border shadow-sm p-3 my-3">'
    context += `<p class="text-muted">${message.authorName}, ${message.createAt}</p>`
    context += `<p>${message.text}</p>`
    context += `<input type="hidden" value="${message.id}" name="message-id">`
    return context
}

let update_awaiting_messages = chat => {
    let context = String()
    chat['awaiting'].forEach(message => {
        context += make_message_template(message)
        context += '<button class="btn btn-outline-secondary m-1 accept-message-btn">Принять</button>'
        context += '<button class="btn btn-outline-secondary m-1 decline-message-btn">Отклонить</button>'
        context += '</div>'
    })
    $('#awaiting-messages').html(context)
}

let update_moderated_messages = chat => {
    let context = String()
    chat['moderated'].forEach(message => {
        context += make_message_template(message)
        context += '<button class="btn btn-outline-danger m-1 delete-message-btn">Удалить</button>'
        context += '</div>'
    })
    $('#moderated-messages').html(context)
}

let update_event_handlers = () => {
    $('.delete-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        console.log(`Deleting <Message ${message_id}> ...`)
    })

    $('.accept-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        console.log(`Accepting <Message ${message_id}> ...`)
    })

    $('.decline-message-btn').click(event => {
        let message_id = $(event.target).siblings('input[name="message-id"]').val()
        console.log(`Declining <Message ${message_id}> ...`)
    })
}

ws.onmessage = event => {
    let data = JSON.parse(event['data'])
    if (data['event'] == 'update_chat') {
        let chat = data['chat']
        update_awaiting_messages(chat)
        update_moderated_messages(chat)
        update_event_handlers()
    }
}
