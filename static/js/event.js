let url = new URL(window.location.href)

$('#widget').click(event => {
    let height = 600, width = 400
    w1 = window.open(`${url.href}/moderated`, 'Moderated chat', `height=${height}, width=${width}, top=0, left=0`)
    w2 = window.open(`${url.href}/awaiting`, 'Awaiting chat', `height=${height}, width=${width}, top=0, left=${width + 20}`)
    if (!w1 || !w2)
    {
        if (!w1 && w2)
            w2.close()
        else if (!w2 && w1)
            w1.close()
        alert('Внимание! У вас отключены всплывающие окна. \nЧтобы продолжить работу включите их')
    }

})
