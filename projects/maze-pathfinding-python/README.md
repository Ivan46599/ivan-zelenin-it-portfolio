# Поиск пути в лабиринте

Алгоритмический Python-проект для поиска пути в текстовом лабиринте.

Задача состоит из двух частей:

1. найти путь от начальной точки до ключа с помощью BFS;
2. найти путь от ключа до выхода с помощью алгоритма A*.

## Стек

- Python;
- collections;
- heapq;
- pathlib;
- argparse;
- pytest.

Внешние библиотеки для основной программы не требуются.

## Алгоритмы

### BFS

Используется для поиска пути от старта до ключа.

### A*

Используется для поиска пути от ключа до выхода.

В качестве эвристики применяется манхэттенское расстояние.

## Структура

```text
maze-pathfinding-python/
├── data/
│   └── sample_maze.txt
├── outputs/
├── src/
│   └── maze_pathfinding.py
├── tests/
│   └── test_maze_pathfinding.py
└── README.md
```

## Запуск

```bash
cd projects/maze-pathfinding-python
```

```bash
python src/maze_pathfinding.py \
    --maze data/sample_maze.txt \
    --output outputs/sample-solved.txt
```

PowerShell:

```powershell
python src/maze_pathfinding.py --maze data/sample_maze.txt --output outputs/sample-solved.txt
```

## Обозначения

Лабиринт может содержать:

```text
A — старт
K — ключ
E — выход
```

После решения маршрут сохраняется в выходной текстовый файл.

## Тестирование

```bash
pytest -q
```

## Что показывает проект

- работу с графами;
- очередь;
- приоритетную очередь;
- BFS;
- A*;
- эвристический поиск;
- чтение и запись файлов;
- декомпозицию программы на функции;
- CLI.