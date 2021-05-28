=========================
Документация разработчика
=========================
***************
Getting Started
***************

Технологический стек:
^^^^^^^^^^^^^^^^^^^^^

- Python 3
- Django 3
- Redis 6

Quickstart
^^^^^^^^^^
Запускаем команды в таком порядке

::

    sudo apt install make
    pip install --upgrade pip
    pip install -r requirements.txt
    docker run -p 6379:6379 -d redis
    ./manage.py migrate
    ./manage.py shell -c "from django.contrib.auth import get_user_model; get_user_model().objects.create_superuser('vasya', '1@abc.net', 'promprog')"
    ./manage.py runserver

"./" можно заменить на "python"

.. toctree::
   :maxdepth: 2
   :caption: Наполнение:

   main.rst
