let url = new URL(window.location.href)
let widget

$('#widget').click(() => {
    if (widget === undefined || widget.closed)
        widget = window.open(`${url.href}/control`, 'Control', `height=${35*vh}, width=${30*vw}, top=5, left=0`)
})
