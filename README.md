### Статус работы workflow
![example workflow](https://github.com/OlesyaSim/foodgram-project-react/actions/workflows/main.yml/badge.svg)

### Описание
REST API для  Foodgram Создан на основе библиотеки Django REST Framework (DRF)

Foodgram - это «Продуктовый помощник»: сайт, на котором пользователи могут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволяет пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

### Посмотреть проект: 
http://51.250.93.22/recipes

http://51.250.93.22/admin/

логин: admin

пароль: admin

### Инструкция по развертыванию
docker-compose exec backend python manage.py migrate 

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic --no-input 

### Используемые технологии

Технологии Python 3.7

Django 3.2.193.2.19 


### Шаблон наполнения env-файла
SECRET_KEY

DEBUG

DB_ENGINE

POSTGRES_DB

POSTGRES_USER

POSTGRES_PASSWORD

DB_HOST

DB_PORT

### Автор
Симутина Олеся

e-mail: olesimka@yandex.ru

https://github.com/OlesyaSim




