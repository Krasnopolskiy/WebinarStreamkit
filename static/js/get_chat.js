'use strict';
// 1. Создаём новый объект XMLHttpRequest
let xhr = new XMLHttpRequest();

// 2. Конфигурируем его: GET-запрос на URL 'https://events.webinar.ru/api/...'
xhr.open('GET', 'https://userapi.webinar.ru/v3/eventsessions/8454277/chat', false);

let timerId = setInterval(function(){
    xhr.setRequestHeader('x-auth-token', 'e779dd59f376abd3993da7009fb1f3f9');
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    // 3. Отсылаем запрос
    xhr.send();

    // 4. Если код ответа сервера не 200, то это ошибка
    if (xhr.status != 200)
      alert( xhr.status + ': ' + xhr.statusText ); // пример вывода: 404: Not Found
    else
        $('#chat').innerHTML = xhr.responseText;

}, 5000);
