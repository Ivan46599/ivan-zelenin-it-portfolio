# Telegram Study Bot

Портфолио-заготовка Telegram-бота для ведения учебных задач. Бот хранит задачи пользователя в SQLite.

## Команды

- `/start` — справка;
- `/add текст задачи` — добавить задачу;
- `/list` — показать задачи;
- `/done id` — отметить задачу выполненной.

## Стек

Python, python-telegram-bot, SQLite, dotenv.

## Запуск

```bash
cd projects/telegram-study-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# вставь токен BotFather в .env
python src/bot.py
```

## Что показывает

Проект демонстрирует работу с внешним API, обработчиками команд, SQLite, конфигурацией через переменные окружения и асинхронной библиотекой.
