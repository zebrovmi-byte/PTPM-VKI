import datetime
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

from delivery_service import calculate_delivery_cost

# Дата отправки зафиксирована в модуле: 2026-09-03
SHIP_DATE = datetime.date(2026, 9, 3)


class TestDeliveryInputValidation(unittest.TestCase):
    """Тесты валидации веса, дистанции и типа посылки."""

    def test_weight_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(0.05, 100, "обычный"), (-1, "0000-00-00"))

    def test_weight_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(50.5, 100, "обычный"), (-1, "0000-00-00"))

    def test_distance_below_minimum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 0, "обычный"), (-1, "0000-00-00"))

    def test_distance_above_maximum_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 5001, "обычный"), (-1, "0000-00-00"))

    def test_unknown_package_type_is_rejected(self):
        self.assertEqual(calculate_delivery_cost(1.0, 100, "скоропортящийся"), (-1, "0000-00-00"))

    def test_boundary_weight_and_distance_are_accepted(self):
        cost, date = calculate_delivery_cost(0.1, 1, "обычный")
        self.assertEqual(cost, 205)
        self.assertEqual(date, "2026-09-04")


class TestDeliveryPricing(unittest.TestCase):
    """Тесты тарифной сетки: базовая ставка, вес, тип упаковки, экспресс."""

    def test_base_cost_is_flat_fee_plus_distance_rate(self):
        # 200 (базовый) + 500 км * 5 = 2700
        cost, _ = calculate_delivery_cost(1.0, 500, "обычный")
        self.assertEqual(cost, 2700)

    def test_medium_weight_applies_twenty_percent_surcharge(self):
        # 6 кг попадает в диапазон (5, 20): 2700 * 1.2 = 3240
        cost, _ = calculate_delivery_cost(6.0, 500, "обычный")
        self.assertEqual(cost, 3240)

    def test_heavy_weight_applies_fifty_percent_surcharge(self):
        # 25 кг >= 20: 2700 * 1.5 = 4050
        cost, _ = calculate_delivery_cost(25.0, 500, "обычный")
        self.assertEqual(cost, 4050)

    def test_exactly_five_kg_should_get_medium_weight_surcharge(self):
        # Граница диапазона: 5 кг должно попадать под коэффициент 1.2
        # (условие weight > 5.0 не включает границу — баг разработчика)
        cost, _ = calculate_delivery_cost(5.0, 500, "обычный")
        self.assertEqual(cost, 3240)

    def test_fragile_package_adds_fixed_fee(self):
        # 2700 + 300 = 3000
        cost, _ = calculate_delivery_cost(1.0, 500, "хрупкий")
        self.assertEqual(cost, 3000)

    def test_dangerous_package_adds_larger_fixed_fee(self):
        # 2700 + 1000 = 3700
        cost, _ = calculate_delivery_cost(1.0, 500, "опасный")
        self.assertEqual(cost, 3700)

    def test_express_delivery_costs_more_than_regular(self):
        # Экспресс-доставка должна быть ДОРОЖЕ обычной (наценка 50%):
        # 2700 * 1.5 = 4050, но модуль умножает стоимость на 0.5 (баг)
        regular, _ = calculate_delivery_cost(1.0, 500, "обычный")
        express, _ = calculate_delivery_cost(1.0, 500, "обычный", is_express=True)
        self.assertGreater(express, regular)

    def test_express_surcharge_is_fifty_percent_of_regular(self):
        regular, _ = calculate_delivery_cost(2.0, 1000, "обычный")
        express, _ = calculate_delivery_cost(2.0, 1000, "обычный", is_express=True)
        self.assertEqual(express, int(regular * 1.5))


class TestDeliveryTime(unittest.TestCase):
    """Тесты расчёта даты доставки (обычной и экспресс)."""

    def test_delivery_date_is_ship_date_plus_days(self):
        # 1500 км -> 1500 // 500 = 3 дня -> 2026-09-06
        _, date = calculate_delivery_cost(1.0, 1500, "обычный")
        self.assertEqual(date, (SHIP_DATE + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))

    def test_short_distance_takes_at_least_one_day(self):
        # 100 км -> max(1, 0) = 1 день
        _, date = calculate_delivery_cost(1.0, 100, "обычный")
        self.assertEqual(date, (SHIP_DATE + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))

    def test_express_delivery_is_faster_than_regular(self):
        _, regular_date = calculate_delivery_cost(1.0, 2000, "обычный")
        _, express_date = calculate_delivery_cost(1.0, 2000, "обычный", is_express=True)
        self.assertLess(
            datetime.date.fromisoformat(express_date),
            datetime.date.fromisoformat(regular_date),
        )

    def test_express_delivery_never_arrives_on_ship_day(self):
        # 300 км -> 1 день -> экспресс: 1 // 2 = 0 дней, доставка «сегодня».
        # Минимальный срок экспресс-доставки — 1 день (баг разработчика).
        _, date = calculate_delivery_cost(1.0, 300, "обычный", is_express=True)
        self.assertGreater(datetime.date.fromisoformat(date), SHIP_DATE)

    def test_express_halves_the_transit_time(self):
        # 3000 км -> 6 дней -> экспресс 3 дня
        _, date = calculate_delivery_cost(1.0, 3000, "обычный", is_express=True)
        self.assertEqual(date, (SHIP_DATE + datetime.timedelta(days=3)).strftime("%Y-%m-%d"))


if __name__ == "__main__":
    unittest.main()
