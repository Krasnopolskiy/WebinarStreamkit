# Webinar Streamkit
Кратко: модератор чата платформы Webinar.ru с возможностью отображения чата в виде отдельной страницы

Web-приложение, позволяющее подключиться к существующей трансляции, проводимой на сайте webinar.ru и 
организовать удобный способ управления модерацией чата.

Требуется 
- доступ к страницам по HTTP (пример: discord streamkit overlay для OBS)
- возможностью ретрансляции сообщений в дискорд (на указанный сервер, в указанный канал)
- страница на сайте, на которой возможно публиковать / отвечать / удалять сообщения, 
  включать и выключать модерацию и т.д. Всё в режиме реального времени.


## Технологический стек:
- Python 3
- Django 3
- Redis 6

## Quickstart
```bash
sudo apt install make
pip install --upgrade pip
pip install -r requirements.txt
docker run -p 6379:6379 -d redis
./manage.py migrate
./manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('vasya', '1@abc.net', 'promprog')"
./manage.py runserver
```

## Read more
- Webinar.ru API: [https://webinar.ru/pres/Web_3.0_API_Description.pdf](https://webinar.ru/pres/Web_3.0_API_Description.pdf)
- Websockets API (Python): [https://websockets.readthedocs.io/en/stable/](https://websockets.readthedocs.io/en/stable/)
- Websockets API (JS): [https://learn.javascript.ru/websocket](https://learn.javascript.ru/websocket) 
