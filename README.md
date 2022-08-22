![example workflow](https://github.com/mvrogozov/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# Проект Foodgram.
***
Проект Foodgram собирает рецепты пользователей.
***

## Возможности.

* Добавление рецепта.
* Подписка на авторов.
* Добавление в избранное.
* Добавление в список покупок и распечатка необходимых ингредиентов.
* Контроль доступа к контенту.
***

## Установка.
***
Клонировать репозиторий и перейти в него в командной строке.

```
git clone git@github.com:mvrogozov/foodgram-project-react.git
```
```
cd foodram-project-react
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Перейти в папку backend

```
cd backend
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
### Возможен запуск в контейнерах Docker

Настройки сервера nginx лежат в файле nginx.conf.
На сервер скопировать файлы docker-compose.yml и nginx.conf, запустить docker-compose:
```
sudo docker-compose up
```
Переменные окружения, необходимые для запуска:

* DB_ENGINE - настройка ENGINE для БД в django.settings
* DB_HOST - имя хоста с БД (в проекте - 'db')
* DB_NAME - имя БД (в проекте - 'postgres')
* DB_PORT - порт для БД
* POSTGRES_PASSWORD - пароль БД
* POSTGRES_USER - пользователь БД

***
Автор:
* Рогозов Михаил