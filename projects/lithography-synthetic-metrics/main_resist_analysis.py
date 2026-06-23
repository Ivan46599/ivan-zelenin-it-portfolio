"""Запуск расчета метрологических параметров модельной структуры фоторезиста."""  

from __future__ import annotations  # Включает отложенную обработку type hints для совместимости.

import csv  
from pathlib import Path  

from resist_metrics import (  # Импортирует функции и классы из локального модуля расчетов.
    SyntheticResistParams,  # Импортирует класс параметров синтетической карты высоты.
    IntensityProfileParams,  # Импортирует класс параметров интенсивностного профиля.
    generate_synthetic_resist,  # Импортирует функцию генерации структуры фоторезиста.
    extract_edges_from_height,  # Импортирует функцию выделения краев по карте высоты.
    calculate_cd_ler_lwr,  # Импортирует функцию расчета CD, LER и LWR.
    generate_intensity_profile,  # Импортирует функцию генерации профиля интенсивности.
    calculate_nils,  # Импортирует функцию расчета NILS.
    save_analysis_plots,  # Импортирует функцию сохранения графиков.
)  


def main() -> None:  # Объявляет главную функцию, которая выполняет весь расчет.
    base_dir = Path(__file__).resolve().parents[1]  # Находит корневую папку проекта относительно текущего файла.
    figures_dir = base_dir / "figures"  # Задает папку для сохранения рисунков.
    data_dir = base_dir / "data"  # Задает папку для сохранения таблицы результатов.
    figures_dir.mkdir(exist_ok=True)  # Создает папку с рисунками, если она отсутствует.
    data_dir.mkdir(exist_ok=True)  # Создает папку с данными, если она отсутствует.

    resist_params = SyntheticResistParams(  # Создает объект параметров модельной структуры фоторезиста.
        nominal_cd_nm=45.0,  # Задает номинальный CD линии в нанометрах.
        line_center_nm=120.0,  # Задает положение центра линии по координате x.
        resist_height_nm=80.0,  # Задает максимальную высоту фоторезиста.
        ler_sigma_nm=1.5,  # Задает целевую шероховатость края в форме sigma.
        edge_correlation_length_nm=10.0,  # Задает длину корреляции шероховатости вдоль линии.
        edge_correlation=0.25,  # Задает корреляцию между шероховатостями левого и правого края.
        sidewall_blur_nm=2.5,  # Задает сглаженность боковых стенок линии.
        height_noise_sigma_nm=1.2,  # Задает уровень шума карты высоты.
        random_seed=7,  # Фиксирует seed для воспроизводимости численного эксперимента.
    )  

    x_grid, y_grid, height_map, truth = generate_synthetic_resist(resist_params)  # Генерирует координатные сетки и карту высоты.
    edges = extract_edges_from_height(x_grid, height_map, threshold_fraction=0.5, min_width_nm=10.0)  # Находит края линии по порогу 50 процентов.
    metrics = calculate_cd_ler_lwr(edges, y_nm=y_grid[:, 0], use_three_sigma=True)  # Рассчитывает CD, LER и LWR по найденным краям.

    intensity_params = IntensityProfileParams(  # Создает параметры модельного профиля интенсивности.
        nominal_cd_nm=resist_params.nominal_cd_nm,  # Передает номинальную ширину линии из модели фоторезиста.
        line_center_nm=resist_params.line_center_nm,  # Передает координату центра линии.
        x_size_nm=resist_params.x_size_nm,  # Передает размер расчетной области по x.
        transition_length_nm=5.0,  # Задает длину перехода интенсивности на краю.
        intensity_min=0.18,  # Задает минимальную интенсивность внутри темной области.
        intensity_max=1.0,  # Задает максимальную интенсивность вне линии.
    )  
    ix, intensity, meta = generate_intensity_profile(intensity_params)  # Генерирует профиль интенсивности и координаты краев.
    nils_left = calculate_nils(ix, intensity, resist_params.nominal_cd_nm, meta["left_edge_nm"])  # Рассчитывает NILS на левом краю.
    nils_right = calculate_nils(ix, intensity, resist_params.nominal_cd_nm, meta["right_edge_nm"])  # Рассчитывает NILS на правом краю.
    metrics["NILS_left"] = nils_left  # Добавляет NILS левого края в словарь результатов.
    metrics["NILS_right"] = nils_right  # Добавляет NILS правого края в словарь результатов.
    metrics["NILS_avg"] = 0.5 * (nils_left + nils_right)  # Добавляет среднее значение NILS по двум краям.

    save_analysis_plots(x_grid, y_grid, height_map, edges, ix, intensity, figures_dir)  # Создает и сохраняет все графики анализа.

    with open(data_dir / "metrics.csv", "w", newline="", encoding="utf-8") as f:  # Открывает CSV-файл для записи результатов.
        writer = csv.writer(f)  # Создает объект writer для построчной записи CSV.
        writer.writerow(["metric", "value"])  # Записывает заголовок таблицы результатов.
        for key, value in metrics.items():  # Последовательно перебирает все рассчитанные метрики.
            writer.writerow([key, value])  # Записывает название метрики и ее численное значение.

    print("Calculated metrics")  
    for key, value in metrics.items():  # Перебирает рассчитанные метрики для печати.
        if isinstance(value, float):  
            print(f"{key}: {value:.4f}")  
        else:  
            print(f"{key}: {value}") 


if __name__ == "__main__":  
    main()  
