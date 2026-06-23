# IT-портфолио — Иван Зеленин

Я студент 3 курса ННГУ им. Н. И. Лобачевского, направление «Фундаментальная информатика и информационные технологии».
Ищу стажировку или junior-позицию в направлениях: Python-разработка, анализ данных, обработка изображений, QA, backend/web-разработка.

В этом репозитории собраны отобранные учебные и портфолио-проекты: Python, SQL, Flask, обработка изображений, численное моделирование, алгоритмы, QA-документация и C# desktop-разработка.

## Ключевые навыки

* Python: скрипты, обработка данных, работа с файлами, CLI, базовая архитектура проекта
* NumPy, pandas, matplotlib, SciPy, Pillow
* SQL: выборки, фильтрация, JOIN, агрегации
* Flask, Jinja2, HTML, CSS, базовая web-разработка
* MATLAB: инженерные и численные расчёты
* Git, GitHub, оформление README и структуры проектов
* Основы QA: чек-листы, тест-кейсы, баг-репорты, Postman
* Английский язык: B1

## Основные проекты

| № | Проект                                                                    | Что демонстрирует                                                                   | Статус                 |
| - | ------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | ---------------------- |
| 1 | [`lithography-real-sem-analysis`](projects/lithography-real-sem-analysis) | Python/MATLAB, обработка SEM/TIF-изображений, расчёт CD/LER/LWR, научные вычисления | основной проект        |
| 2 | [`lithography-synthetic-metrics`](projects/lithography-synthetic-metrics) | NumPy, моделирование структуры фоторезиста, расчёт CD/LER/LWR/NILS, графики         | основной проект        |
| 3 | [`restaurant-booking-flask`](projects/restaurant-booking-flask)           | Flask, Jinja2, SQL, формы, CRUD, web-приложение                                     | web/database проект    |
| 4 | [`maze-pathfinding-python`](projects/maze-pathfinding-python)             | алгоритмы поиска пути, BFS/A*, работа с файлами, CLI                                | алгоритмический проект |
| 5 | [`student-performance-analysis`](projects/student-performance-analysis)   | pandas, NumPy, matplotlib, CSV-анализ, отчёт                                        | data analysis проект   |
| 6 | [`qa-portfolio`](projects/qa-portfolio)                                   | чек-листы, тест-кейсы, баг-репорты, API-тестирование                                | Junior QA портфолио    |

## Дополнительные проекты

| Проект                                                            | Описание                                                                 |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------ |
| [`api-data-parser`](projects/api-data-parser)                     | пример CLI-скрипта для получения JSON-данных, обработки и выгрузки в CSV |
| [`telegram-study-bot`](projects/telegram-study-bot)               | учебный Telegram-бот с SQLite и `.env`-конфигурацией                     |
| [`sql-airline-queries`](projects/sql-airline-queries)             | SQL-запросы: JOIN, группировки, фильтрация, агрегаты                     |
| [`csharp-winforms-reference`](projects/csharp-winforms-reference) | примеры C# WinForms-приложений                                           |

## Быстрый запуск Python-проектов

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Установка зависимостей:

```bash
pip install -r requirements.txt
```

Дальше нужно открыть README конкретного проекта и выполнить команды запуска из него.

## Структура репозитория

```text
ivan-zelenin-it-portfolio/
├── README.md
├── requirements.txt
├── resume/
│   ├── Ivan_Zelenin_IT_resume.md
│   └── Ivan_Zelenin_IT_resume.docx
├── career/
│   ├── INTERNSHIP_ROADMAP.md
│   ├── WHERE_TO_APPLY.md
│   ├── GITHUB_UPLOAD_GUIDE.md
│   └── COVER_LETTERS.md
└── projects/
    ├── lithography-real-sem-analysis
    ├── lithography-synthetic-metrics
    ├── restaurant-booking-flask
    ├── maze-pathfinding-python
    ├── student-performance-analysis
    ├── api-data-parser
    ├── telegram-study-bot
    ├── qa-portfolio
    ├── sql-airline-queries
    └── csharp-winforms-reference
```

## Резюме

Резюме находится в папке [`resume/`](resume/):

* `Ivan_Zelenin_IT_resume.md` — версия в Markdown
* `Ivan_Zelenin_IT_resume.docx` — версия для отправки работодателю

## Контакты

* Email: [i.k.zelenin@gmail.com](mailto:i.k.zelenin@gmail.com)
* Город: Нижний Новгород
* GitHub: Ivan46599
