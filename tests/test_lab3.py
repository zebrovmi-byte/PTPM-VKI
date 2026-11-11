import unittest
from unittest.mock import MagicMock, patch
from src.main import DeliveryCalculator, DatabaseManager, ConsoleUserInterface, EmailNotifier, DeliveryController


class TestLab3Integration(unittest.TestCase):

    def setUp(self):
        # Используем БД в памяти для тестов
        self.db = DatabaseManager(":memory:")
        self.calculator = DeliveryCalculator()

    def tearDown(self):
        self.db.close()

    # --- ИНТЕГРАЦИОННЫЕ ТЕСТЫ (3 шт) ---

    @patch.object(ConsoleUserInterface, 'get_user_input', return_value=(10.0, 100.0, False))
    @patch.object(EmailNotifier, 'send_notification')
    def test_integration_new_calculation_saves_to_db_and_notifies(self, mock_notify, mock_ui):
        """Интеграционный тест 1: Новый расчет (расчет -> БД -> отправка уведомления)."""
        ui = ConsoleUserInterface()
        notifier = EmailNotifier()
        controller = DeliveryController(self.calculator, self.db, ui, notifier)

        result = controller.process_delivery_request()

        # Проверки сквозного сценария
        self.assertEqual(result, 800.0)
        self.assertEqual(self.db.get_result(10.0, 100.0, False), 800.0)
        mock_notify.assert_called_once_with("Расчет выполнен. Итоговая стоимость: 800.0 руб.")

    @patch.object(ConsoleUserInterface, 'get_user_input', return_value=(5.0, 50.0, True))
    @patch.object(EmailNotifier, 'send_notification')
    def test_integration_uses_cached_value_from_db(self, mock_notify, mock_ui):
        """Интеграционный тест 2: Повторный запрос берет данные из БД без повторного расчета."""
        # Предзаполняем БД
        self.db.add_result(5.0, 50.0, True, 750.0)

        # Подменяем калькулятор моком, чтобы убедиться, что вычисление НЕ вызывалось
        mock_calc = MagicMock()
        ui = ConsoleUserInterface()
        notifier = EmailNotifier()
        controller = DeliveryController(mock_calc, self.db, ui, notifier)

        result = controller.process_delivery_request()

        self.assertEqual(result, 750.0)
        mock_calc.calculate.assert_not_called()  # Проверка, что вычисление пропущено
        mock_notify.assert_called_once()

    @patch('builtins.input', side_effect=['2.0', '10.0', 'n'])
    def test_integration_ui_with_controller(self, mock_input):
        """Интеграционный тест 3: Проверка реального взаимодействия ConsoleUserInterface с патчем input()."""
        ui = ConsoleUserInterface()
        notifier = MagicMock()
        controller = DeliveryController(self.calculator, self.db, ui, notifier)

        result = controller.process_delivery_request()

        # 200 + 2*10 + 10*5 = 270.0
        self.assertEqual(result, 270.0)
        self.assertEqual(self.db.get_result(2.0, 10.0, False), 270.0)


    # --- МОДУЛЬНЫЕ ТЕСТЫ БД И ВАЛИДАЦИИ (2 шт) ---

    def test_db_crud_operations(self):
        """Модульный тест: Создание, получение и удаление записей из БД."""
        self.db.add_result(1.0, 1.0, False, 215.0)
        self.assertEqual(self.db.get_result(1.0, 1.0, False), 215.0)

        self.db.delete_result(1.0, 1.0, False)
        self.assertIsNone(self.db.get_result(1.0, 1.0, False))

    def test_calculator_invalid_values_raise_error(self):
        """Модульный тест: Валидация входных данных в калькуляторе."""
        with self.assertRaises(ValueError):
            self.calculator.calculate(-5.0, 100.0)


if __name__ == "__main__":
    unittest.main()