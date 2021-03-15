'use strict';
// 1. Создаём новый объект XMLHttpRequest
let xhr = new XMLHttpRequest();

// 2. Конфигурируем его: GET-запрос на URL 'phones.json'
xhr.open('GET', 'https://events.webinar.ru/api/eventsessions/8454277/chat', false);

// 3. Отсылаем запрос
xhr.send();

// 4. Если код ответа сервера не 200, то это ошибка
if (xhr.status != 200)
  alert( xhr.status + ': ' + xhr.statusText ); // пример вывода: 404: Not Found
else
    $('#chat').innerHTML += xhr.responseText;
/*let socket = new WebSocket("wss://ping-m9.webinar.ru/socketcluster/", [],
    {
        'headers': {
                'Cookie': 'bpmRef=events.webinar.ru; bpmHref=https://webinar.ru/; bpmTrackingId=a871fe33-c23a-a321-f76b-07ce76bebcd8; popmechanic_sbjs_migrations=popmechanic_1418474375998%3D1%7C%7C%7C1471519752600%3D1%7C%7C%7C1471519752605%3D1; intercom-id-eb4dv2rj=0d21ea2a-1df3-49b9-ac4e-9d2823c0d7cf; intercom-session-eb4dv2rj=QUIyWVUzNytFbDlwTXBMOGw3ZGMyNThsVWs0aDd6SUtKdVJQelJ4ZGJUZWsrTTlIUzRjQy9EZW5DZ1BmcEhjRS0tQmYrSVJCWXk2RWxMcnR5dkhGWGQ2dz09--5154490107546fdd7818d4bfdc6feed50b8148d4'
            }
    }
);

socket.onopen = function() {
  alert("Соединение установлено.");
};
socket.onclose = function(event) {
  if (event.wasClean) {
    alert('Соединение закрыто чисто');
  } else {
    alert('Обрыв соединения'); // например, "убит" процесс сервера
  }
  alert('Код: ' + event.code + ' причина: ' + event.reason);
};

socket.onmessage = function(event) {
    $('#chat').innerHTML += event.data + '<br>';
};

socket.onerror = function(error) {
  alert("Ошибка " + error.message);
};
*/
