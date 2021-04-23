let url = new URL(window.location.href)
let widget

$('#widget').click(() => {
    if (widget === undefined || widget.closed)
        widget = window.open(`${url.href}/control`, 'Control', `height=${280}, width=${420}, top=5, left=0`)
})
