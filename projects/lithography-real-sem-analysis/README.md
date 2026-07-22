# Анализ SEM-изображений фоторезиста

Инженерно-научный Python-проект для автоматического анализа реальных SEM/TIF-изображений проявленного фоторезиста.

Основная задача — обработать изображение, определить положение линий и рассчитать метрологические параметры **CD, LER и LWR**.

## Что делает программа

1. Загружает SEM/TIF/PNG/JPG-изображения.
2. Исключает служебные области изображения.
3. Определяет масштаб изображения в `nm/px`.
4. Нормализует контраст.
5. Находит вертикальные элементы фоторезиста.
6. Определяет левый и правый край каждой линии.
7. Рассчитывает:
   - CD;
   - LER;
   - LWR.
8. Сохраняет результаты в CSV.
9. Строит диагностические графики.

## Стек

- Python;
- NumPy;
- SciPy;
- Pillow;
- matplotlib;
- argparse;
- dataclasses.

Также в проекте сохранена MATLAB-реализация для сравнения результатов.

## Структура проекта

```text
lithography-real-sem-analysis/
├── python/
│   ├── analyze_real_resist_images.py
│   └── resist_image_metrics.py
├── matlab/
├── input_images/
├── results/
├── figures/
├── requirements.txt
└── README.md
```

## Установка

Перейдите в папку проекта:

```bash
cd projects/lithography-real-sem-analysis
```

Создайте виртуальное окружение:

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

Установите зависимости:

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python python/analyze_real_resist_images.py \
    --input-dir input_images \
    --results-dir results \
    --figures-dir figures
```

В PowerShell команду также можно записать одной строкой:

```powershell
python python/analyze_real_resist_images.py --input-dir input_images --results-dir results --figures-dir figures
```

## Результаты

Программа создаёт:

```text
results/summary_metrics.csv
results/per_line_metrics.csv
results/section_edges.csv
```

А также диагностические изображения в папке:

```text
figures/
```

Пример результата для одного из сохранённых изображений:

- средний CD: около `35.04 nm`;
- LWR σ: около `2.46 nm`;
- средний LER σ: около `1.74 nm`.

## Пример визуализации

![Выделение краёв](figures/fig_005%281%29_edges_overlay.png)

![Распределение ширины](figures/fig_005%281%29_width_histogram.png)

## Почему этот проект важен

Проект объединяет:

- Python;
- обработку изображений;
- численные методы;
- анализ данных;
- визуализацию;
- работу с инженерной предметной областью;
- экспорт воспроизводимых результатов.

## Ограничения

NILS не рассчитывается непосредственно по SEM-изображению, поскольку SEM-изображение проявленного фоторезиста не является оптическим профилем интенсивности.

Для расчёта NILS используется отдельный модельный проект:

[`../lithography-synthetic-metrics`](../lithography-synthetic-metrics)

## План развития

- добавить автоматические тесты для вычислительных функций;
- разделить обработку изображения и CLI;
- добавить тестовые синтетические изображения;
- добавить автоматическую проверку проекта через CI.