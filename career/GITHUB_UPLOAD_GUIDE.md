# Как залить портфолио на GitHub

## Вариант 1: один общий репозиторий

Подходит на первом этапе, если нужно быстро показать все работы.

```bash
git init
git add .
git commit -m "Initial IT portfolio"
git branch -M main
git remote add origin https://github.com/USERNAME/ivan-zelenin-it-portfolio.git
git push -u origin main
```

## Вариант 2: отдельные репозитории — лучше для резюме

Создай отдельные репозитории:

1. `lithography-real-sem-analysis`
2. `lithography-synthetic-metrics`
3. `restaurant-booking-flask`
4. `maze-pathfinding-python`
5. `student-performance-analysis`

В резюме лучше давать ссылки именно на 3–5 отдельных репозиториев, а не на папку с десятками лабораторных.

## Что обязательно должно быть в каждом репозитории

- `README.md` с описанием задачи;
- стек технологий;
- инструкция запуска;
- скриншоты/графики результата;
- `requirements.txt`, если это Python;
- `.gitignore`;
- отсутствие секретов, паролей, токенов;
- нормальные имена файлов на латинице.

## Что не загружать

- `venv`, `.venv`;
- `__pycache__`;
- `.vs`, `bin`, `obj`;
- `.exe`, `.dll`, `.pdb`;
- чужие учебники и методички;
- файлы с паролями;
- слабые `hello_world`-работы.
