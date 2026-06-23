# Restaurant Booking Flask App

Учебное web-приложение ресторана с меню, галереей, контактной формой, бронированием столиков и административным просмотром заявок.

## Возможности

- главная страница с популярными блюдами;
- меню по категориям;
- галерея;
- форма обратной связи;
- бронирование столиков;
- автоматическая очистка истёкших броней;
- административный просмотр бронирований.

## Стек

Python, Flask, Jinja2, SQL, HTML, CSS, JavaScript.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app app run --debug
```

Для Linux/macOS активация окружения:

```bash
source .venv/bin/activate
```

## Структура

```text
app.py          # Flask-приложение
config.py       # конфигурация
static/         # CSS, JS, изображения
templates/      # HTML/Jinja2-шаблоны
utils/          # вспомогательные функции
```

## Что показывает проект

Проект демонстрирует базовый full-stack: маршруты Flask, шаблоны Jinja2, формы, SQL-запросы, конфигурацию и работу с web-интерфейсом.
