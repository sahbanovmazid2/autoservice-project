"""Проверка входных данных автосервиса."""
from datetime import date
import re


def require_text(value, field='Поле', max_length=150):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field}: значение не может быть пустым')
    value = value.strip()
    if len(value) > max_length:
        raise ValueError(f'{field}: слишком длинное значение')
    return value


def validate_phone(phone):
    phone = require_text(phone, 'Телефон', 25)
    if not re.fullmatch(r'\+?[0-9 ()-]{10,25}', phone):
        raise ValueError('Некорректный номер телефона')
    if len(re.sub(r'\D', '', phone)) < 10:
        raise ValueError('Телефон должен содержать не менее 10 цифр')
    return phone


def validate_plate(plate):
    return require_text(plate, 'Госномер', 15).upper()


def validate_year(year):
    if type(year) is not int or not 1950 <= year <= date.today().year + 1:
        raise ValueError('Недопустимый год выпуска')
    return year


def validate_price(price):
    if isinstance(price, bool) or not isinstance(price, (int, float)) or not 0 <= price <= 10_000_000:
        raise ValueError('Стоимость должна быть неотрицательным числом')
    return round(float(price), 2)


def validate_quantity(quantity):
    if type(quantity) is not int or not 1 <= quantity <= 1000:
        raise ValueError('Количество должно быть от 1 до 1000')
    return quantity


def calculate_total(price, quantity=1):
    return round(validate_price(price) * validate_quantity(quantity), 2)


def validate_order_status(status):
    if status not in ('новый', 'в работе', 'готов', 'выдан'):
        raise ValueError('Недопустимый статус заказ-наряда')
    return status
