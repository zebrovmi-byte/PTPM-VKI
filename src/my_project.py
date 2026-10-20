import logging
import sys
import os
import math

LOG_FORMAT = "%(asctime)s | [%(levelname)-7s] | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(level=logging.DEBUG):
    """Настраивает логгер: вывод в консоль и в файл logs/file_txt.log.

    Вынос конфигурации в отдельную функцию (баг ЛР1: настройка логгера
    выполнялась при импорте модуля, из-за чего при подключении модуля
    в юнит-тесты создавалась папка logs и перенастраивался root-логгер).
    """
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        datefmt=DATE_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8"),
        ],
        force=True,
    )


logger = logging.getLogger(__name__)


def process_triangle(side1, side2, side3):
    eps = 1e-9

    try:
        a = float(side1)
        b = float(side2)
        c = float(side3)
    except (ValueError, TypeError):
        logger.error(f"Некорректные данные (не числа): {side1}, {side2}, {side3}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    # Баг ЛР1: nan/inf проходили все сравнения (все сравнения с nan — False)
    # и попадали в расчёт координат; теперь отсекаемся сразу.
    if not (math.isfinite(a) and math.isfinite(b) and math.isfinite(c)):
        logger.error(f"Стороны должны быть конечными числами: {a}, {b}, {c}")
        return "", [(-2, -2), (-2, -2), (-2, -2)]

    if a <= 0 or b <= 0 or c <= 0:
        logger.error(f"Стороны должны быть положительными: {a}, {b}, {c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if a + b <= c + eps or a + c <= b + eps or b + c <= a + eps:
        logger.info(f"Не треугольник: стороны {a}, {b}, {c}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    if abs(a - b) < eps and abs(b - c) < eps:
        tip = "равносторонний"
    elif abs(a - b) < eps or abs(a - c) < eps or abs(b - c) < eps:
        tip = "равнобедренный"
    else:
        tip = "разносторонний"

    try:
        max_side = max(a, b, c)
        scale = 90 / max_side

        x = (a * a + c * c - b * b) / (2 * c)
        h = math.sqrt(max(0.0, a * a - x * x))

        x1 = 5
        y1 = 95
        x2 = int(5 + c * scale)
        y2 = 95
        x3 = int(5 + x * scale)
        y3 = int(95 - h * scale)

        coords = [(x1, y1), (x2, y2), (x3, y3)]
    except Exception as e:
        logger.error(f"Ошибка при расчёте координат: {a}, {b}, {c}. {e}")
        return "не треугольник", [(-1, -1), (-1, -1), (-1, -1)]

    logger.info(f"Успех: стороны={side1}, {side2}, {side3}, тип={tip}, координаты={coords}")
    return tip, coords


if __name__ == "__main__":
    configure_logging()
    logger.info("Логгер успешно сконфигурирован")
    logger.info("Приложение запущено")

    print("Введите три стороны треугольника (или 'exit' для выхода)")
    print("-" * 50)

    while True:
        side1 = input("Сторона A: ").strip()
        if side1.lower() == "exit":
            print("Выход из программы")
            break

        side2 = input("Сторона B: ").strip()
        if side2.lower() == "exit":
            print("Выход из программы")
            break

        side3 = input("Сторона C: ").strip()
        if side3.lower() == "exit":
            print("Выход из программы")
            break

        tip, coords = process_triangle(side1, side2, side3)

        print()
        print(f"Тип треугольника: {tip if tip else '(пустая строка — нечисловые данные)'}")
        print(f"Координаты: {coords}")
        print("-" * 50)
