from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from database import add_task, connect, init_db, list_tasks, mark_done

load_dotenv()
DB_PATH = Path(os.getenv('DATABASE_PATH', 'study_bot.sqlite3'))


def get_conn():
    conn = connect(DB_PATH)
    init_db(conn)
    return conn


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Привет. Я бот для учебных задач. Команды: /add текст, /list, /done id'
    )


async def add(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    title = ' '.join(context.args).strip()
    if not title:
        await update.message.reply_text('Напиши задачу после команды: /add подготовить резюме')
        return
    with get_conn() as conn:
        task_id = add_task(conn, update.effective_user.id, title)
    await update.message.reply_text(f'Задача #{task_id} добавлена')


async def list_(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with get_conn() as conn:
        tasks = list_tasks(conn, update.effective_user.id)
    if not tasks:
        await update.message.reply_text('Список задач пуст')
        return
    lines = []
    for task in tasks:
        marker = '✅' if task['is_done'] else '⬜'
        lines.append(f"{marker} #{task['id']}: {task['title']}")
    await update.message.reply_text('\n'.join(lines))


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text('Используй формат: /done 1')
        return
    task_id = int(context.args[0])
    with get_conn() as conn:
        ok = mark_done(conn, update.effective_user.id, task_id)
    await update.message.reply_text('Готово' if ok else 'Задача не найдена')


def main() -> None:
    token = os.getenv('BOT_TOKEN')
    if not token:
        raise RuntimeError('Set BOT_TOKEN in .env')
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('add', add))
    app.add_handler(CommandHandler('list', list_))
    app.add_handler(CommandHandler('done', done))
    app.run_polling()


if __name__ == '__main__':
    main()
