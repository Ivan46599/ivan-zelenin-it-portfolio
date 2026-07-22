# Парсер JSON/API-данных

CLI-программа на Python для загрузки данных из JSON-файла или HTTP API, нормализации записей, фильтрации и сохранения результата в CSV.

## Возможности

- загрузка локального JSON;
- получение JSON через HTTP;
- проверка базовой структуры;
- нормализация записей;
- фильтрация по минимальной зарплате;
- фильтрация только удалённых вакансий;
- сохранение результата в CSV;
- запуск через аргументы командной строки.

## Стек

- Python;
- requests;
- JSON;
- CSV;
- argparse;
- pathlib;
- pytest.

## Структура

```text
api-data-parser/
├── data/
│   └── sample_jobs.json
├── outputs/
│   └── jobs.csv
├── src/
│   └── parse_jobs.py
├── tests/
│   └── test_parse_jobs.py
├── requirements.txt
└── README.md
```

## Установка

```bash
cd projects/api-data-parser
pip install -r requirements.txt
```

## Запуск на локальном JSON

```bash
python src/parse_jobs.py \
    --source data/sample_jobs.json \
    --output outputs/jobs.csv
```

PowerShell:

```powershell
python src/parse_jobs.py --source data/sample_jobs.json --output outputs/jobs.csv
```

## Фильтрация

Например, выбрать только удалённые вакансии с зарплатой от 50000:

```bash
python src/parse_jobs.py \
    --source data/sample_jobs.json \
    --output outputs/filtered_jobs.csv \
    --min-salary 50000 \
    --remote-only
```

## HTTP API

Вместо локального файла параметру `--source` можно передать HTTP/HTTPS URL, возвращающий JSON-массив объектов.

## Тестирование

```bash
pytest -q
```

## Что показывает проект

Проект демонстрирует типичный ETL-подобный сценарий:

```text
источник данных
↓
JSON
↓
нормализация
↓
фильтрация
↓
CSV
```

## План развития

- обработка сетевых ошибок;
- логирование;
- повторные HTTP-запросы;
- поддержка пагинации;
- расширение набора тестов.