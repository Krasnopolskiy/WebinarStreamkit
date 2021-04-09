let url = new URL(window.location.href)

$('#widget').click(event => {
    window.open(`${url.href}/moderated`, 'Moderated chat', 'height=600, width=300')
    window.open(`${url.href}/awaiting`, 'Awaiting chat', 'height=600, width=300')
})
