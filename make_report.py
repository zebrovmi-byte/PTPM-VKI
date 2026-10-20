# -*- coding: utf-8 -*-
"""Генерация отчёта по ЛР2 (Отчет_ЛР2_Зебров.docx)."""
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH

doc = Document()

style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)

def h(text, level=1):
    p = doc.add_heading(text, level=level)
    for run in p.runs:
        run.font.name = "Times New Roman"
    return p

def p(text, bold=False):
    par = doc.add_paragraph()
    run = par.add_run(text)
    run.bold = bold
    return par

title = doc.add_heading("Отчёт по лабораторной работе №2", level=0)
for run in title.runs:
    run.font.name = "Times New Roman"
p("Тема: Юнит-тестирование проектов и автоматизация проверок")
p("Курс: ПТПМ-ВКИ, ветка Lab_2 репозитория PTPM-VKI")
p("Инструмент: встроенный модуль unittest (Python 3.12), запуск:")
par = doc.add_paragraph()
run = par.add_run('python -m unittest discover -s tests -p "test_*.py" -v')
run.font.name = "Consolas"
run.font.size = Pt(11)

# ---------------- Пункт А ----------------
h("Пункт А. Общее количество тестов и статистика прохождения", 1)
p("Всего написано 34 автономных юнит-теста в двух файлах:")
p("• tests/test_my_project.py — 17 тестов к коду из ЛР1 (модуль src/my_project.py, анализ треугольников);")
p("• tests/test_delivery.py — 17 тестов к предоставленному модулю доставки (src/delivery_service.py).")

table_a = doc.add_table(rows=3, cols=5)
table_a.style = "Table Grid"
hdr = ["Модуль", "Тестов", "Прошло", "Упало", "Итог"]
rows = [
    ["src/my_project.py (ЛР1)", "17", "17", "0", "OK"],
    ["src/delivery_service.py (доставка)", "17", "13", "4", "FAILED (failures=4)"],
]
for j, text in enumerate(hdr):
    table_a.rows[0].cells[j].text = text
for i, row in enumerate(rows, start=1):
    for j, text in enumerate(row):
        table_a.rows[i].cells[j].text = text

p("")
p("Общий результат прогона: Ran 34 tests — FAILED (failures=4).", bold=True)
p("Перед прогоном в коде ЛР1 были найдены и исправлены два бага (см. раздел «Исправления в коде ЛР1»), "
  "после чего все 17 собственных тестов проходят успешно. Код модуля доставки намеренно НЕ исправлялся: "
  "заданием предусмотрена фиксация расхождений в отчёте.")

# ---------------- Пункт Б ----------------
h("Пункт Б. Количество упавших тестов для кода доставки", 1)
p("Для кода доставки (src/delivery_service.py, исходный Delivery.py) упали 4 теста из 17:", bold=True)
p("1. test_exactly_five_kg_should_get_medium_weight_surcharge;")
p("2. test_express_delivery_costs_more_than_regular;")
p("3. test_express_surcharge_is_fifty_percent_of_regular;")
p("4. test_express_delivery_never_arrives_on_ship_day.")
p("Все четыре падения указывают на три дефекта в логике разработчика (два теста ловят один и тот же баг "
  "экспресс-наценки с разных сторон).")

# ---------------- Пункт В ----------------
h("Пункт В. Локализация аномалий", 1)
p("Бизнес-требования, восстановленные по контексту модуля (документация, названия переменных, "
  "комментарий TODO): базовая ставка 200 ₽ + 5 ₽/км; весовые коэффициенты 1.2 (от 5 до 20 кг) "
  "и 1.5 (от 20 кг); наценка за хрупкий +300 ₽ и опасный +1000 ₽; экспресс-доставка ДОРОЖЕ обычной "
  "на 50% и выполняется вдвое быстрее, но не быстрее чем за 1 день.")

table_v = doc.add_table(rows=1, cols=5)
table_v.style = "Table Grid"
hdr_v = ["№", "Упавший тест", "Строка delivery_service.py", "Дефект в логике", "Вариант исправления"]
for j, text in enumerate(hdr_v):
    table_v.rows[0].cells[j].text = text

rows_v = [
    ["1",
     "test_exactly_five_kg_should_get_medium_weight_surcharge",
     "строка 25: if weight > 5.0 and weight < 20.0:",
     "Граница weight = 5.0 не входит в диапазон среднего веса: условие строгое «>», поэтому посылка "
     "ровно 5 кг не получает коэффициент 1.2 и стоит 2700 ₽ вместо 3240 ₽. Соседняя ветка использует "
     "weight >= 20.0 (граница включена), что подтверждает несогласованность.",
     "Заменить строгое сравнение на включающее: if weight >= 5.0 and weight < 20.0:"],
    ["2",
     "test_express_delivery_costs_more_than_regular",
     "строка 36: total_cost *= 0.5",
     "Экспресс-доставка УДЕШЕВЛЯЕТ стоимость вдвое вместо наценки: обычный тариф 2700 ₽, экспресс — "
     "1350 ₽. Бизнес-логика требует, чтобы экспресс был дороже обычного (наценка 50%), а не дешевле.",
     "Заменить коэффициент скидки на коэффициент наценки: total_cost *= 1.5"],
    ["3",
     "test_express_surcharge_is_fifty_percent_of_regular",
     "строка 36: total_cost *= 0.5",
     "Тот же баг, проверенный числом: для 2 кг / 1000 км ожидается 1.5 × 7800 = 11700 ₽, модуль "
     "возвращает 2600 ₽ (0.5 × 5200). Некорректна сама величина и знак коэффициента.",
     "Заменить коэффициент скидки на коэффициент наценки: total_cost *= 1.5"],
    ["4",
     "test_express_delivery_never_arrives_on_ship_day",
     "строка 44: days_needed = days_needed // 2",
     "Целочисленное деление обнуляет срок: при 300 км days_needed = 1, экспресс: 1 // 2 = 0 дней — "
     "доставка «в день отправки», что невозможно даже для экспресс-тарифа (минимум 1 день). "
     "Для чётных сроков деление корректно (6 → 3), поэтому баг проявляется только на коротких "
     "дистанциях и при нечётных сроках (5 → 2 вместо ожидаемых 3 при округлении вверх).",
     "Гарантировать минимальный срок и корректное округление: days_needed = max(1, -(-days_needed // 2)) "
     "(или days_needed = max(1, days_needed // 2), если допустимо округление вниз)"],
]
for row in rows_v:
    cells = table_v.add_row().cells
    for j, text in enumerate(row):
        cells[j].text = text

p("")
p("Ширина колонок таблицы настроена под страницу:")
for row in table_v.rows:
    row.cells[0].width = Cm(0.8)
    row.cells[1].width = Cm(4.0)
    row.cells[2].width = Cm(3.5)
    row.cells[3].width = Cm(6.0)
    row.cells[4].width = Cm(4.5)

# ---------------- Исправления в ЛР1 ----------------
h("Дополнительно. Исправленные баги в коде ЛР1 (src/my_project.py)", 1)
p("1. Обработка TypeError в валидации ввода. Исходный код перехватывал только ValueError: float(None) "
  "бросает TypeError, и тест test_none_input_returns_empty_result_marker падал с исключением вместо "
  "возврата маркера (-2, -2). Исправление: except (ValueError, TypeError).")
p("2. Защита от нечисловых значений nan/inf. Значение nan проходило все проверки (сравнения с nan дают "
  "False) и попадало в расчёт координат, что приводило к некорректному результату. Исправление: "
  "дополнительная проверка math.isfinite() для всех трёх сторон.")
p("3. Побочный эффект при импорте. Настройка логгера и создание папки logs выполнялась на уровне модуля, "
  "из-за чего импорт модуля в тестах перенастраивал root-логгер и создавал файлы. Исправление: "
  "конфигурация вынесена в функцию configure_logging(), которая вызывается только при запуске скрипта "
  "напрямую (__main__).")

doc.save("Отчет_ЛР2_Зебров.docx")
print("OK")
