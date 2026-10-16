import pytest
from validators import (validate_phone, validate_year, validate_price,
                        validate_quantity, validate_plate, require_text, calculate_total,
                        validate_order_status)


@pytest.mark.parametrize('year', [1950, 1999, 2020])
def test_year_valid(year):
    assert validate_year(year) == year


@pytest.mark.parametrize('year', [1949, -1, 0, '2020', None, True, 2020.5])
def test_year_invalid(year):
    with pytest.raises(ValueError):
        validate_year(year)


@pytest.mark.parametrize('price', [0, 100, 1999.99, 10_000_000])
def test_price_valid(price):
    assert validate_price(price) >= 0


@pytest.mark.parametrize('price', [-1, -0.01, '100', None, True, 10_000_001])
def test_price_invalid(price):
    with pytest.raises(ValueError):
        validate_price(price)


@pytest.mark.parametrize('quantity', [0, -1, 1001, 1.5, True, None])
def test_quantity_invalid(quantity):
    with pytest.raises(ValueError):
        validate_quantity(quantity)


def test_phone_and_plate():
    assert validate_phone('+79001234567') == '+79001234567'
    assert validate_plate('а123вс77') == 'А123ВС77'


def test_invalid_phone():
    with pytest.raises(ValueError):
        validate_phone('123')


def test_empty_name():
    with pytest.raises(ValueError):
        require_text('   ')


def test_total():
    assert calculate_total(1250, 3) == 3750


def test_invalid_status():
    with pytest.raises(ValueError):
        validate_order_status('отменён')
