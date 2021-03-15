'use strict';
let socket = new WebSocket("wss://msg-edge-12.webinar.ru/engine.io/?EIO=3&transport=websocket");
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
