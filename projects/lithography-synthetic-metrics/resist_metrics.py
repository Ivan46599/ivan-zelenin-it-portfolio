"""Модуль для генерации модельной структуры фоторезиста и расчета метрик литографии."""  

from __future__ import annotations  # Включает отложенную обработку type hints для совместимости и удобства.

from dataclasses import dataclass  # Импортирует декоратор для компактного описания классов параметров.
from pathlib import Path  # Импортирует объектный интерфейс для работы с путями к файлам и папкам.
from typing import Dict, Tuple  # Импортирует типы словаря и кортежа для аннотаций функций.

import numpy as np  
import matplotlib.pyplot as plt  


@dataclass  # Автоматически создает init и другие служебные методы для класса параметров.
class SyntheticResistParams:  # Описывает набор параметров синтетической карты высоты фоторезиста.
    pixel_size_nm: float = 1.0  # Задает шаг пространственной сетки по x и y в нанометрах.
    x_size_nm: float = 240.0  # Задает размер расчетной области по координате x в нанометрах.
    y_size_nm: float = 500.0  # Задает размер расчетной области по координате y в нанометрах.
    nominal_cd_nm: float = 45.0  # Задает номинальную ширину линии, то есть ожидаемый CD.
    line_center_nm: float = 120.0  # Задает положение центра линии по координате x.
    resist_height_nm: float = 80.0  # Задает максимальную высоту проявленного фоторезиста.
    ler_sigma_nm: float = 1.5  # Задает среднеквадратическую шероховатость каждого края.
    edge_correlation_length_nm: float = 10.0  # Задает длину корреляции шероховатости вдоль линии.
    edge_correlation: float = 0.25  # Задает степень корреляции между левым и правым краем.
    sidewall_blur_nm: float = 2.5  # Задает сглаженность боковой стенки в модели высоты.
    height_noise_sigma_nm: float = 1.2  # Задает стандартное отклонение шума карты высоты.
    random_seed: int = 7  # Фиксирует генератор случайных чисел для воспроизводимости результата.


@dataclass  # Автоматически создает init и другие служебные методы для параметров профиля интенсивности.
class IntensityProfileParams:  # Описывает параметры модельного интенсивностного профиля для NILS.
    nominal_cd_nm: float = 45.0  # Задает номинальную ширину линии, используемую в формуле NILS.
    line_center_nm: float = 120.0  # Задает положение центра линии на оси x.
    x_size_nm: float = 240.0  # Задает длину одномерной расчетной области по x.
    pixel_size_nm: float = 0.2  # Задает шаг дискретизации интенсивностного профиля.
    intensity_min: float = 0.18  # Задает минимальную нормированную интенсивность внутри темной области.
    intensity_max: float = 1.0  # Задает максимальную нормированную интенсивность вне линии.
    transition_length_nm: float = 5.0  # Задает характерную длину перехода интенсивности на краю.


def _gaussian_kernel(sigma_px: float, radius_factor: float = 4.0) -> np.ndarray:  # Создает одномерное гауссово ядро сглаживания.
    if sigma_px <= 0:  # Проверяет случай нулевой или отрицательной ширины сглаживания.
        return np.array([1.0])  # Возвращает единичное ядро, которое не изменяет сигнал.
    radius = max(1, int(np.ceil(radius_factor * sigma_px)))  # Вычисляет радиус ядра в пикселях.
    x = np.arange(-radius, radius + 1)  # Формирует дискретные координаты ядра от -radius до +radius.
    kernel = np.exp(-0.5 * (x / sigma_px) ** 2)  # Вычисляет значения гауссовой функции.
    kernel /= kernel.sum()  # Нормирует ядро, чтобы сумма коэффициентов была равна единице.
    return kernel  # Возвращает готовое ядро сглаживания.


def _smooth_noise(noise: np.ndarray, sigma_px: float) -> np.ndarray:  # Сглаживает случайный шум для задания коррелированной шероховатости.
    kernel = _gaussian_kernel(sigma_px)  # Создает гауссово ядро с заданной шириной в пикселях.
    return np.convolve(noise, kernel, mode="same")  # Выполняет свертку и сохраняет исходную длину массива.


def generate_synthetic_resist(params: SyntheticResistParams) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, np.ndarray]]:  # Генерирует модельную карту высоты линии фоторезиста.
    """Создает карту высоты одной линии фоторезиста и истинные положения ее краев."""  # Описывает физический смысл функции.
    rng = np.random.default_rng(params.random_seed)  # Создает генератор случайных чисел с фиксированным seed.
    x = np.arange(0, params.x_size_nm + params.pixel_size_nm, params.pixel_size_nm)  # Формирует координаты x.
    y = np.arange(0, params.y_size_nm + params.pixel_size_nm, params.pixel_size_nm)  # Формирует координаты y.
    x_grid, y_grid = np.meshgrid(x, y)  # Создает двумерные координатные сетки для карты высоты.

    n_y = len(y)  # Определяет количество строк карты высоты.
    raw_common = rng.normal(0.0, 1.0, n_y)  # Генерирует общую шумовую составляющую для обоих краев.
    raw_left = rng.normal(0.0, 1.0, n_y)  # Генерирует независимую шумовую составляющую левого края.
    raw_right = rng.normal(0.0, 1.0, n_y)  # Генерирует независимую шумовую составляющую правого края.
    sigma_px = params.edge_correlation_length_nm / params.pixel_size_nm  # Переводит длину корреляции из нанометров в пиксели.

    common = _smooth_noise(raw_common, sigma_px)  # Сглаживает общую составляющую шероховатости.
    left_ind = _smooth_noise(raw_left, sigma_px)  # Сглаживает независимую составляющую левого края.
    right_ind = _smooth_noise(raw_right, sigma_px)  # Сглаживает независимую составляющую правого края.

    def normalize(arr: np.ndarray) -> np.ndarray:  # Внутренняя функция нормировки массива на стандартное отклонение.
        std = np.std(arr)  # Вычисляет стандартное отклонение массива.
        if std == 0:  # Проверяет случай постоянного массива без разброса.
            return arr  # Возвращает массив без изменений, чтобы избежать деления на ноль.
        return arr / std  # Нормирует массив так, чтобы стандартное отклонение стало равно единице.

    common = normalize(common)  # Нормирует общую составляющую шероховатости.
    left_ind = normalize(left_ind)  # Нормирует независимую составляющую левого края.
    right_ind = normalize(right_ind)  # Нормирует независимую составляющую правого края.

    rho = np.clip(params.edge_correlation, 0.0, 0.95)  # Ограничивает коэффициент корреляции физически допустимым диапазоном.
    left_rough = params.ler_sigma_nm * (np.sqrt(rho) * common + np.sqrt(1.0 - rho) * left_ind)  # Формирует шероховатость левого края.
    right_rough = params.ler_sigma_nm * (np.sqrt(rho) * common + np.sqrt(1.0 - rho) * right_ind)  # Формирует шероховатость правого края.

    nominal_left = params.line_center_nm - params.nominal_cd_nm / 2.0  # Вычисляет номинальную координату левого края.
    nominal_right = params.line_center_nm + params.nominal_cd_nm / 2.0  # Вычисляет номинальную координату правого края.
    left_edge = nominal_left + left_rough  # Добавляет шероховатость к левому краю.
    right_edge = nominal_right + right_rough  # Добавляет шероховатость к правому краю.

    blur = max(params.sidewall_blur_nm, 1e-9)  # Ограничивает параметр размытия снизу, чтобы избежать деления на ноль.
    left_transition = 1.0 / (1.0 + np.exp(-(x_grid - left_edge[:, None]) / blur))  # Строит плавный переход на левом краю.
    right_transition = 1.0 / (1.0 + np.exp((x_grid - right_edge[:, None]) / blur))  # Строит плавный переход на правом краю.
    height = params.resist_height_nm * left_transition * right_transition  # Получает высоту линии как произведение двух переходов.
    height += rng.normal(0.0, params.height_noise_sigma_nm, size=height.shape)  # Добавляет шум измерения высоты.
    height = np.clip(height, 0.0, None)  # Убирает отрицательные значения высоты, которые физически невозможны.

    truth = {  # Создает словарь с истинными параметрами модельной структуры.
        "left_edge_nm": left_edge,  # Сохраняет истинное положение левого края.
        "right_edge_nm": right_edge,  # Сохраняет истинное положение правого края.
        "width_nm": right_edge - left_edge,  # Сохраняет истинную локальную ширину линии.
        "x_nm": x,  # Сохраняет одномерную координатную сетку x.
        "y_nm": y,  # Сохраняет одномерную координатную сетку y.
    }  
    return x_grid, y_grid, height, truth  # Возвращает сетки, карту высоты и истинные значения для контроля.


def _interpolated_crossing(x: np.ndarray, values: np.ndarray, threshold: float, idx_low: int, idx_high: int) -> float:  # Уточняет координату пересечения профиля с порогом.
    x0, x1 = x[idx_low], x[idx_high]  # Берет координаты двух соседних точек вокруг порога.
    v0, v1 = values[idx_low], values[idx_high]  # Берет значения профиля в этих двух точках.
    if v1 == v0:  # Проверяет случай одинаковых значений, когда интерполяция неопределенна.
        return float(0.5 * (x0 + x1))  # Возвращает середину интервала как устойчивую оценку.
    return float(x0 + (threshold - v0) * (x1 - x0) / (v1 - v0))  # Выполняет линейную интерполяцию координаты порога.


def extract_edges_from_height(  # Начинает определение функции выделения краев по карте высоты.
    x_grid: np.ndarray,  # Принимает двумерную сетку координат x.
    height_map: np.ndarray,  # Принимает двумерную карту высоты фоторезиста.
    threshold_fraction: float = 0.5,  # Задает долю от максимальной высоты для выбора порога.
    min_width_nm: float = 5.0,  # Задает минимально допустимую ширину найденной линии.
) -> Dict[str, np.ndarray]:  # Возвращает словарь массивов с найденными краями и ширинами.
    """Выделяет левый и правый край линии по заданному порогу высоты."""  
    x = x_grid[0, :]  # Берет координаты x из первой строки сетки.
    threshold = threshold_fraction * float(np.nanmax(height_map))  # Вычисляет абсолютный порог высоты.
    left_edges = []  # Создает список для координат левого края.
    right_edges = []  # Создает список для координат правого края.
    row_indices = []  # Создает список индексов строк, где край был найден.

    for row_idx, row in enumerate(height_map):  # Последовательно обрабатывает каждую строку карты высоты.
        above = row >= threshold  # Создает булев массив точек, расположенных выше порога.
        if not np.any(above):  # Проверяет, есть ли в строке хотя бы одна точка линии.
            continue  
        indices = np.flatnonzero(above)  # Получает индексы всех точек, превышающих порог.
        left_i = int(indices[0])  # Берет первый индекс как грубое положение левого края.
        right_i = int(indices[-1])  # Берет последний индекс как грубое положение правого края.
        if right_i <= left_i:  # Проверяет, что найденная область имеет ненулевую ширину.
            continue  

        if left_i > 0:  # Проверяет, можно ли интерполировать левый край по предыдущей точке.
            left_x = _interpolated_crossing(x, row, threshold, left_i - 1, left_i)  # Уточняет координату левого края.
        else:  
            left_x = float(x[left_i])  # Использует координату первой найденной точки без интерполяции.
        if right_i < len(x) - 1:  # Проверяет, можно ли интерполировать правый край по следующей точке.
            right_x = _interpolated_crossing(x, row, threshold, right_i + 1, right_i)  # Уточняет координату правого края.
        else:  
            right_x = float(x[right_i])  # Использует координату последней найденной точки без интерполяции.

        if right_x - left_x >= min_width_nm:  # Отбрасывает слишком узкие объекты, похожие на шум.
            left_edges.append(left_x)  # Добавляет координату левого края в список результатов.
            right_edges.append(right_x)  # Добавляет координату правого края в список результатов.
            row_indices.append(row_idx)  # Сохраняет номер строки, соответствующий найденным краям.

    left_edges = np.asarray(left_edges)  # Преобразует список левых краев в массив NumPy.
    right_edges = np.asarray(right_edges)  # Преобразует список правых краев в массив NumPy.
    row_indices = np.asarray(row_indices)  # Преобразует список строк в массив NumPy.
    widths = right_edges - left_edges  # Вычисляет локальную ширину линии для каждой строки.

    return {  
        "left_edge_nm": left_edges,  # Возвращает массив координат левого края.
        "right_edge_nm": right_edges,  # Возвращает массив координат правого края.
        "width_nm": widths,  # Возвращает массив локальных ширин линии.
        "row_indices": row_indices,  # Возвращает индексы строк с корректно найденными краями.
        "threshold_nm": threshold,  # Возвращает использованное абсолютное значение порога.
    }  


def _detrend(values: np.ndarray, coordinate: np.ndarray | None = None) -> Tuple[np.ndarray, np.ndarray]:  # Удаляет линейный тренд из массива координат края.
    if coordinate is None:  # Проверяет, передана ли независимая координата.
        coordinate = np.arange(len(values), dtype=float)  # Использует номера точек, если координата не задана.
    if len(values) < 2:  # Проверяет, достаточно ли точек для построения прямой.
        return values - np.mean(values), np.array([0.0, np.mean(values)])  # Возвращает отклонение от среднего для короткого массива.
    coeffs = np.polyfit(coordinate, values, deg=1)  # Аппроксимирует край линейной функцией.
    trend = np.polyval(coeffs, coordinate)  # Вычисляет значения найденного линейного тренда.
    return values - trend, coeffs  # Возвращает остатки без тренда и коэффициенты прямой.


def calculate_cd_ler_lwr(edges: Dict[str, np.ndarray], y_nm: np.ndarray | None = None, use_three_sigma: bool = True) -> Dict[str, float]:  # Рассчитывает CD, LER и LWR по найденным краям.
    left = edges["left_edge_nm"]  # Извлекает массив координат левого края.
    right = edges["right_edge_nm"]  # Извлекает массив координат правого края.
    width = edges["width_nm"]  # Извлекает массив локальных ширин линии.
    rows = edges.get("row_indices", np.arange(len(width)))  # Получает номера строк или создает их при отсутствии.
    if y_nm is not None:  # Проверяет, передана ли физическая координата y.
        coord = y_nm[rows]  # Использует физические координаты y для удаления тренда.
    else: 
        coord = rows.astype(float)  # Использует индексы строк как независимую координату.

    left_residual, _ = _detrend(left, coord)  # Удаляет линейный тренд из положения левого края.
    right_residual, _ = _detrend(right, coord)  # Удаляет линейный тренд из положения правого края.

    cd = float(np.mean(width))  # Вычисляет среднюю ширину линии, то есть CD.
    lwr_sigma = float(np.std(width, ddof=1)) if len(width) > 1 else 0.0  # Вычисляет стандартное отклонение ширины.
    ler_left_sigma = float(np.std(left_residual, ddof=1)) if len(left_residual) > 1 else 0.0  # Вычисляет LER левого края.
    ler_right_sigma = float(np.std(right_residual, ddof=1)) if len(right_residual) > 1 else 0.0  # Вычисляет LER правого края.
    ler_avg_sigma = 0.5 * (ler_left_sigma + ler_right_sigma)  # Усредняет шероховатость двух краев.

    factor = 3.0 if use_three_sigma else 1.0  # Выбирает форму вывода: sigma или 3 sigma.
    return {  
        "CD_mean_nm": cd,  # Сохраняет среднее значение CD.
        "CD_std_nm": lwr_sigma,  # Сохраняет стандартное отклонение ширины как разброс CD.
        "LWR_sigma_nm": lwr_sigma,  # Сохраняет LWR в форме одного стандартного отклонения.
        "LWR_3sigma_nm": 3.0 * lwr_sigma,  # Сохраняет LWR в форме 3 sigma.
        "LER_left_sigma_nm": ler_left_sigma,  # Сохраняет LER левого края в форме sigma.
        "LER_right_sigma_nm": ler_right_sigma,  # Сохраняет LER правого края в форме sigma.
        "LER_avg_sigma_nm": ler_avg_sigma,  # Сохраняет среднюю LER двух краев в форме sigma.
        "LER_avg_3sigma_nm": 3.0 * ler_avg_sigma,  # Сохраняет среднюю LER двух краев в форме 3 sigma.
        "reported_LWR_nm": factor * lwr_sigma,  # Сохраняет LWR в выбранной форме представления.
        "reported_LER_nm": factor * ler_avg_sigma,  # Сохраняет LER в выбранной форме представления.
        "samples_count": int(len(width)),  # Сохраняет количество строк, участвовавших в расчете.
    }  


def generate_intensity_profile(params: IntensityProfileParams) -> Tuple[np.ndarray, np.ndarray, Dict[str, float]]:  # Создает модельный профиль интенсивности для NILS.
    """Создает одномерный профиль интенсивности, похожий на воздушное изображение."""  # Поясняет назначение функции.
    x = np.arange(0, params.x_size_nm + params.pixel_size_nm, params.pixel_size_nm)  # Формирует сетку координаты x.
    left = params.line_center_nm - params.nominal_cd_nm / 2.0  # Вычисляет положение левого номинального края.
    right = params.line_center_nm + params.nominal_cd_nm / 2.0  # Вычисляет положение правого номинального края.
    s = max(params.transition_length_nm, 1e-9)  # Ограничивает длину перехода снизу для устойчивости.

    inside_left = 1.0 / (1.0 + np.exp(-(x - left) / s))  # Формирует плавный вход в область линии слева.
    inside_right = 1.0 / (1.0 + np.exp((x - right) / s))  # Формирует плавный выход из области линии справа.
    inside = inside_left * inside_right  # Получает маску внутренней области линии.
    intensity = params.intensity_max - (params.intensity_max - params.intensity_min) * inside  # Строит профиль с минимумом внутри линии.
    meta = {"left_edge_nm": left, "right_edge_nm": right}  # Сохраняет координаты номинальных краев для расчета NILS.
    return x, intensity, meta  # Возвращает координаты, интенсивность и метаданные профиля.


def calculate_nils(x_nm: np.ndarray, intensity: np.ndarray, nominal_cd_nm: float, edge_position_nm: float) -> float:  # Рассчитывает NILS на заданном краю.
    """Вычисляет NILS = CD * |d(ln I) / dx| в окрестности номинального края."""  # Записывает используемую формулу.
    intensity_safe = np.clip(intensity, 1e-12, None)  # Заменяет нулевые значения малым положительным числом.
    log_i = np.log(intensity_safe)  # Вычисляет натуральный логарифм интенсивности.
    derivative = np.gradient(log_i, x_nm)  # Численно вычисляет производную d(ln I) / dx.
    idx = int(np.argmin(np.abs(x_nm - edge_position_nm)))  # Находит индекс точки, ближайшей к заданному краю.
    return float(nominal_cd_nm * abs(derivative[idx]))  # Возвращает нормированную логарифмическую крутизну.


def save_analysis_plots(  # Начинает определение функции сохранения графиков анализа.
    x_grid: np.ndarray,  # Принимает двумерную сетку координат x.
    y_grid: np.ndarray,  # Принимает двумерную сетку координат y.
    height_map: np.ndarray,  # Принимает карту высоты фоторезиста.
    edges: Dict[str, np.ndarray],  # Принимает словарь с найденными краями и ширинами.
    intensity_x: np.ndarray,  # Принимает координаты интенсивностного профиля.
    intensity: np.ndarray,  # Принимает значения интенсивностного профиля.
    output_dir: str | Path,  # Принимает путь к папке для сохранения рисунков.
) -> Dict[str, str]:  # Возвращает словарь с путями к сохраненным рисункам.
    """Сохраняет стандартные графики, используемые в отчете."""  
    output_dir = Path(output_dir)  # Преобразует путь к папке в объект Path.
    output_dir.mkdir(parents=True, exist_ok=True)  # Создает папку для рисунков, если ее еще нет.
    paths: Dict[str, str] = {}  # Создает словарь для путей к сохраненным файлам.

    y_nm = y_grid[:, 0]  # Извлекает физические координаты y из первой колонки сетки.
    rows = edges["row_indices"]  # Извлекает индексы строк, где были найдены края.

    fig, ax = plt.subplots(figsize=(8, 5))  # Создает фигуру для карты высоты и краев.
    im = ax.imshow(  # Отображает карту высоты как двумерное изображение.
        height_map,  # Передает массив высот для визуализации.
        extent=[x_grid.min(), x_grid.max(), y_grid.max(), y_grid.min()],  # Задает физические границы осей.
        aspect="auto",  # Разрешает автоматическое соотношение сторон.
        origin="upper",  # Устанавливает начало изображения в верхней части.
    )  
    ax.plot(edges["left_edge_nm"], y_nm[rows], linewidth=1.2, label="left edge")  # Наносит найденный левый край на карту.
    ax.plot(edges["right_edge_nm"], y_nm[rows], linewidth=1.2, label="right edge")  # Наносит найденный правый край на карту.
    ax.set_xlabel("x, nm")  # Подписывает ось x.
    ax.set_ylabel("y, nm")  # Подписывает ось y.
    ax.set_title("Synthetic resist height map and extracted edges")  # Добавляет заголовок графика.
    ax.legend(loc="upper right")  # Добавляет легенду в правый верхний угол.
    fig.colorbar(im, ax=ax, label="height, nm")  # Добавляет цветовую шкалу высоты.
    fig.tight_layout()  # Автоматически корректирует отступы на рисунке.
    paths["height_edges"] = str(output_dir / "height_map_edges.png")  # Формирует путь для первого рисунка.
    fig.savefig(paths["height_edges"], dpi=220)  # Сохраняет карту высоты с краями в файл.
    plt.close(fig)  # Закрывает фигуру и освобождает память.

    fig, ax = plt.subplots(figsize=(8, 4))  # Создает фигуру для графика ширины вдоль линии.
    ax.plot(y_nm[rows], edges["width_nm"], linewidth=1.2)  # Строит зависимость локальной ширины от координаты y.
    ax.set_xlabel("y, nm")  # Подписывает ось y-координаты линии.
    ax.set_ylabel("line width, nm")  # Подписывает ось локальной ширины.
    ax.set_title("Line width along the structure")  # Добавляет заголовок графика ширины.
    ax.grid(True, alpha=0.35)  # Включает сетку для удобства чтения графика.
    fig.tight_layout()  # Корректирует отступы перед сохранением.
    paths["width_along_y"] = str(output_dir / "width_along_y.png")  # Формирует путь для графика ширины.
    fig.savefig(paths["width_along_y"], dpi=220)  # Сохраняет график ширины в файл.
    plt.close(fig)  

    fig, ax = plt.subplots(figsize=(7, 4))  # Создает фигуру для гистограммы ширин.
    ax.hist(edges["width_nm"], bins=30, density=False)  # Строит гистограмму локальных ширин линии.
    ax.set_xlabel("line width, nm")  # Подписывает ось значений ширины.
    ax.set_ylabel("count")  # Подписывает ось количества наблюдений.
    ax.set_title("Width distribution")  # Добавляет заголовок гистограммы.
    ax.grid(True, alpha=0.35)  # Включает сетку на гистограмме.
    fig.tight_layout()  # Корректирует отступы изображения.
    paths["width_hist"] = str(output_dir / "width_histogram.png")  # Формирует путь для гистограммы.
    fig.savefig(paths["width_hist"], dpi=220)  # Сохраняет гистограмму в файл.
    plt.close(fig)  

    fig, ax = plt.subplots(figsize=(8, 4))  # Создает фигуру для интенсивностного профиля.
    ax.plot(intensity_x, intensity, linewidth=1.4)  # Строит модельный профиль интенсивности.
    ax.set_xlabel("x, nm")  # Подписывает ось координаты x.
    ax.set_ylabel("normalized intensity")  # Подписывает ось нормированной интенсивности.
    ax.set_title("Modeled intensity profile for NILS calculation")  # Добавляет заголовок графика NILS.
    ax.grid(True, alpha=0.35)  # Включает сетку для чтения профиля.
    fig.tight_layout()  # Корректирует отступы перед сохранением.
    paths["intensity_profile"] = str(output_dir / "intensity_profile.png")  # Формирует путь для профиля интенсивности.
    fig.savefig(paths["intensity_profile"], dpi=220)  # Сохраняет профиль интенсивности в файл.
    plt.close(fig) 

    return paths  # Возвращает словарь путей ко всем сохраненным рисункам.
