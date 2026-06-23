# Telegram Study Bot

Учебный Telegram-бот для заметок и напоминаний. Проект показывает работу с обработчиками команд, SQLite и конфигурацией через переменные окружения.

## Возможности

- обработка базовых команд;
- сохранение учебных заметок;
- хранение данных в SQLite;
- конфигурация токена через `.env`;
- разделение кода на модули.

## Стек

Python, aiogram или python-telegram-bot, SQLite, python-dotenv.

## Запуск

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python bot.py
```

В `.env` нужно указать токен бота.

## Что показывает проект

Проект демонстрирует работу с внешним API, хранением данных и базовой архитектурой небольшого Python-приложения.
