iziToast.settings({
    position: 'bottomRight',
})

messages.forEach(message => {
    let payload = { message: message.message }
    switch (message.tags) {
        case 'green':
            iziToast.success(payload)
            break;
        case 'blue':
            iziToast.info(payload)
            break;
        case 'yellow':
            iziToast.warning(payload)
            break;
        case 'red':
            iziToast.error(payload)
            break;
    }
})
