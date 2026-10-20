import math
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from my_project import process_triangle


class TestTriangleTypeDetection(unittest.TestCase):
    """Тесты определения типа треугольника по трём сторонам."""

    def test_equilateral_triangle_is_detected(self):
        tip, _ = process_triangle(3, 3, 3)
        self.assertEqual(tip, "равносторонний")

    def test_isosceles_triangle_is_detected(self):
        tip, _ = process_triangle(5, 5, 8)
        self.assertEqual(tip, "равнобедренный")

    def test_scalene_triangle_is_detected(self):
        tip, _ = process_triangle(3, 4, 5)
        self.assertEqual(tip, "разносторонний")

    def test_equilateral_triangle_with_float_sides_is_detected(self):
        tip, _ = process_triangle(2.5, 2.5, 2.5)
        self.assertEqual(tip, "равносторонний")


class TestTriangleValidation(unittest.TestCase):
    """Тесты валидации входных данных."""

    def test_zero_side_is_rejected_as_non_triangle(self):
        tip, coords = process_triangle(0, 4, 5)
        self.assertEqual(tip, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_negative_side_is_rejected_as_non_triangle(self):
        tip, coords = process_triangle(-3, 4, 5)
        self.assertEqual(tip, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_triangle_inequality_violation_is_rejected(self):
        # 1 + 2 <= 3 — нарушено неравенство треугольника
        tip, coords = process_triangle(1, 2, 3)
        self.assertEqual(tip, "не треугольник")
        self.assertEqual(coords, [(-1, -1), (-1, -1), (-1, -1)])

    def test_degenerate_triangle_with_sum_equal_to_third_side_is_rejected(self):
        # Вырожденный треугольник: 2 + 3 == 5
        tip, _ = process_triangle(2, 3, 5)
        self.assertEqual(tip, "не треугольник")

    def test_non_numeric_input_returns_empty_result_marker(self):
        tip, coords = process_triangle("abc", 4, 5)
        self.assertEqual(tip, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_none_input_returns_empty_result_marker(self):
        # Баг ЛР1: float(None) бросает TypeError, который не перехватывался
        # (обрабатывался только ValueError), и тест падал с исключением.
        tip, coords = process_triangle(None, 4, 5)
        self.assertEqual(tip, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_nan_input_returns_empty_result_marker(self):
        # Баг ЛР1: nan проходил все сравнения (False) и попадал в расчёт координат
        tip, coords = process_triangle(float("nan"), 4, 5)
        self.assertEqual(tip, "")
        self.assertEqual(coords, [(-2, -2), (-2, -2), (-2, -2)])

    def test_numeric_strings_are_accepted(self):
        tip, _ = process_triangle("3", "4", "5")
        self.assertEqual(tip, "разносторонний")


class TestTriangleCoordinates(unittest.TestCase):
    """Тесты расчёта координат треугольника для отрисовки."""

    def test_coordinates_are_scaled_to_fit_100x100_canvas(self):
        _, coords = process_triangle(3, 4, 5)
        for x, y in coords:
            self.assertTrue(0 <= x <= 100, f"x={x} вне холста")
            self.assertTrue(0 <= y <= 100, f"y={y} вне холста")

    def test_base_of_triangle_lies_on_bottom_line(self):
        _, coords = process_triangle(7, 8, 9)
        (x1, y1), (x2, y2), _ = coords
        self.assertEqual(y1, 95)
        self.assertEqual(y2, 95)
        self.assertEqual(x1, 5)
        self.assertGreater(x2, x1)

    def test_coordinates_are_integer_pairs(self):
        _, coords = process_triangle(13, 14, 15)
        self.assertEqual(len(coords), 3)
        for point in coords:
            self.assertEqual(len(point), 2)
            for value in point:
                self.assertIsInstance(value, int)


if __name__ == "__main__":
    unittest.main()
