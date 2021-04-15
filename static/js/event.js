let url = new URL(window.location.href)

$('#widget').click(event => {
    let height = 600, width = 400
    let params = 'height=600, width=400, top=0, left=0'
    w1 = window.open(`${url.href}/moderated`, 'Moderated chat', params)
    w2 = window.open(`${url.href}/awaiting`, 'Awaiting chat', params)
    if (w1 === null || w2 === null)
    {
        if (w2 !== null)
            w2.close()
        if (w1 !== null)
            w1.close()
        iziToast.error({ message: 'Чтобы продолжить работу, включите всплывающие окна.' })
    }
})
