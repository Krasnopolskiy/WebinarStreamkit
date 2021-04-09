let url = new URL(window.location.href)

$('#widget').click(event => {
    let height = 600, width = 400
    window.open(`${url.href}/moderated`, 'Moderated chat', `height=${height}, width=${width}, top=0, left=0`)
    window.open(`${url.href}/awaiting`, 'Awaiting chat', `height=${height}, width=${width}, top=0, left=${width + 20}`)
})
