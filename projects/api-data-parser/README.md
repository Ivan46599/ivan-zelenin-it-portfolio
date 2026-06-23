# API Data Parser

Портфолио-проект: загрузка JSON-данных из файла или API, нормализация полей, фильтрация и экспорт в CSV.

## Стек

Python, requests, csv, argparse, JSON.

## Запуск

```bash
cd projects/api-data-parser
pip install requests
python src/parse_jobs.py --source data/sample_jobs.json --remote-only --min-salary 45000
```

## Что показывает работодателю

Проект показывает базовую backend/data-автоматизацию: работа с HTTP, JSON, CLI-аргументами, фильтрацией и CSV-выгрузкой.
