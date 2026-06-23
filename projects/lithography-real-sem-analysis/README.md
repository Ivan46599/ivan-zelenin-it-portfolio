# Lithography Real SEM Analysis

Инженерно-научный проект для анализа реальных SEM/TIF-изображений проявленного фоторезиста. Цель — автоматически выделять линии на изображениях, калибровать масштаб и рассчитывать метрологические параметры CD, LER и LWR.

## Что делает проект

1. Загружает SEM/TIF/PNG/JPG-изображения.
2. Удаляет служебную область микроскопа и верхние подписи из области анализа.
3. Оценивает масштаб `nm/px` по scale bar или использует заданную калибровку.
4. Нормализует контраст SEM-изображения.
5. Находит тёмные или светлые вертикальные элементы фоторезиста.
6. Извлекает левый и правый край каждой линии по строкам.
7. Рассчитывает:
   - CD — critical dimension;
   - LWR — line width roughness;
   - LER — line edge roughness.
8. Сохраняет CSV-таблицы и диагностические графики.

## Стек

Python, NumPy, SciPy, Pillow, matplotlib, dataclasses, argparse. Дополнительно приложена MATLAB-реализация.

## Запуск Python-версии

```bash
pip install numpy scipy pillow matplotlib
python python/analyze_real_resist_images.py --input-dir input_images --results-dir results --figures-dir figures
```

## Структура

```text
python/        # Python-реализация анализа
matlab/        # MATLAB-аналоги функций
input_images/  # SEM/TIF-изображения
results/       # CSV-таблицы с рассчитанными метриками
figures/       # диагностические графики
```

## Ограничения

NILS не рассчитывается по SEM-изображению, потому что SEM после проявления не является оптическим intensity profile. NILS корректно считать по optical/air-image intensity profile или соответствующей симуляции.

