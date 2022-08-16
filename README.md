![example workflow](https://github.com/mvrogozov/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
# praktikum_new_diplom
http://51.250.18.154/
admin
qwaszxcv
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

Для этого в папке foodgram-project-react/infra/
запустить docker-compose. Настройки сервера nginx лежат в файле nginx.conf

***
Автор:
* Рогозов Михаил