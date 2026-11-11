from abc import ABC, abstractmethod
import sqlite3


# a. Класс вычислений / валидации (Логика из ЛР1/ЛР2)
class DeliveryCalculator:
    """Класс вычислений стоимости доставки."""

    def calculate(self, weight: float, distance: float, is_express: bool = False) -> float:
        if weight <= 0 or distance <= 0:
            raise ValueError("Вес и расстояние должны быть больше нуля")

        base_rate = 200.0
        cost = base_rate + (weight * 10.0) + (distance * 5.0)

        if is_express:
            cost *= 1.5

        return round(cost, 2)


# b. Класс работы с базой данных (SQLite)
class DatabaseManager:
    """Класс для взаимодействия с БД SQLite."""

    def __init__(self, db_name: str = ":memory:"):
        self.conn = sqlite3.connect(db_name)
        self.create_table()

    def create_table(self):
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS delivery_cache (
                    weight REAL,
                    distance REAL,
                    is_express INTEGER,
                    cost REAL,
                    PRIMARY KEY (weight, distance, is_express)
                )
            """)

    def get_result(self, weight: float, distance: float, is_express: bool):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT cost FROM delivery_cache WHERE weight=? AND distance=? AND is_express=?",
            (weight, distance, int(is_express))
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def add_result(self, weight: float, distance: float, is_express: bool, cost: float):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO delivery_cache VALUES (?, ?, ?, ?)",
                (weight, distance, int(is_express), cost)
            )

    def delete_result(self, weight: float, distance: float, is_express: bool):
        with self.conn:
            self.conn.execute(
                "DELETE FROM delivery_cache WHERE weight=? AND distance=? AND is_express=?",
                (weight, distance, int(is_express))
            )

    def close(self):
        self.conn.close()


# c. Класс взаимодействия с пользователем (Интерфейс)
class UserInterface(ABC):
    @abstractmethod
    def get_user_input(self) -> tuple[float, float, bool]:
        pass


class ConsoleUserInterface(UserInterface):
    def get_user_input(self) -> tuple[float, float, bool]:
        weight = float(input("Введите вес (кг): "))
        distance = float(input("Введите расстояние (км): "))
        express_str = input("Экспресс-доставка? (y/n): ").strip().lower()
        is_express = express_str == 'y'
        return weight, distance, is_express


# d. Класс сторонней зависимости (Интерфейс уведомлений/email)
class ExternalNotifier(ABC):
    @abstractmethod
    def send_notification(self, message: str) -> bool:
        pass


class EmailNotifier(ExternalNotifier):
    def send_notification(self, message: str) -> bool:
        # Имитация внешней зависимости (отправка email)
        print(f"[Email Server]: {message}")
        return True


# e. Класс-контроллер (Controller)
class DeliveryController:
    """Контроллер, реализующий бизнес-логику сквозного сценария."""

    def __init__(self, calculator: DeliveryCalculator, db: DatabaseManager, ui: UserInterface,
                 notifier: ExternalNotifier):
        self.calculator = calculator
        self.db = db
        self.ui = ui
        self.notifier = notifier

    def process_delivery_request(self):
        # 1. Запрос данных у пользователя
        weight, distance, is_express = self.ui.get_user_input()

        # 2. Проверка базы данных (Кэш)
        cached_cost = self.db.get_result(weight, distance, is_express)

        if cached_cost is not None:
            cost = cached_cost
        else:
            # Если записи нет — вычисляем и сохраняем в БД
            cost = self.calculator.calculate(weight, distance, is_express)
            self.db.add_result(weight, distance, is_express, cost)

        # 3. Отправка результата сторонней зависимости
        msg = f"Расчет выполнен. Итоговая стоимость: {cost} руб."
        self.notifier.send_notification(msg)

        # 4. Возврат результата
        return cost