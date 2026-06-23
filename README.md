# IT-портфолио — Иван Зеленин

Репозиторий собран как единое портфолио студента технического направления: Python, обработка изображений, численное моделирование, SQL, web-разработка, алгоритмы, QA-документация и базовые C# desktop-проекты.

> Важное замечание: часть проектов — исходные учебные/лабораторные работы, часть — аккуратно оформленные портфолио-заготовки для демонстрации навыков. Перед отправкой работодателю нужно уметь объяснить каждый проект и при необходимости запустить его локально.

## Рекомендуемый порядок показа работодателю

| № | Проект | Что демонстрирует | Статус |
|---|---|---|---|
| 1 | `projects/lithography-real-sem-analysis` | Python, MATLAB, обработка SEM/TIF-изображений, CD/LER/LWR, научные вычисления | основной проект |
| 2 | `projects/lithography-synthetic-metrics` | NumPy, моделирование структуры фоторезиста, NILS, LER/LWR/CD, графики | основной проект |
| 3 | `projects/restaurant-booking-flask` | Flask, Jinja2, MySQL/SQL, формы, CRUD, web-приложение | использовать после проверки схемы БД |
| 4 | `projects/maze-pathfinding-python` | алгоритмы поиска пути, BFS/A*, работа с файлами, CLI | добавлен рефакторинг |
| 5 | `projects/student-performance-analysis` | pandas, NumPy, matplotlib, CSV-анализ, отчёт | портфолио-заготовка |
| 6 | `projects/api-data-parser` | requests, JSON, CSV, обработка API-данных | портфолио-заготовка |
| 7 | `projects/telegram-study-bot` | Telegram Bot API, SQLite, dotenv, обработчики команд | портфолио-заготовка |
| 8 | `projects/qa-portfolio` | тест-кейсы, чек-листы, баг-репорты, Postman collection | для Junior QA |
| 9 | `projects/sql-airline-queries` | SQL-запросы, JOIN, агрегации, выборки | дополнительный проект |
| 10 | `projects/csharp-winforms-reference` | C#, WinForms, desktop UI | дополнительный материал |

## Как превратить в GitHub-портфолио

Оптимальный вариант — не выкладывать всё одним огромным репозиторием, а создать отдельные репозитории для 4–5 сильных проектов:

1. `lithography-real-sem-analysis`
2. `lithography-synthetic-metrics`
3. `restaurant-booking-flask`
4. `maze-pathfinding-python`
5. `student-performance-analysis` или `api-data-parser`

Остальное можно оставить в этом монорепозитории как архив учебных и портфолио-проектов.

## Быстрый запуск Python-проектов

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Дальше смотри README внутри каждого проекта.

## Документы

- `resume/Ivan_Zelenin_IT_resume.md` — текст резюме.
- `resume/Ivan_Zelenin_IT_resume.docx` — готовый DOCX для отправки.
- `career/INTERNSHIP_ROADMAP.md` — пошаговый план подготовки к стажировке.
- `career/WHERE_TO_APPLY.md` — площадки и компании для поиска стажировок.
- `career/GITHUB_UPLOAD_GUIDE.md` — как залить проекты на GitHub.

Дата сборки: 2026-06-23.
