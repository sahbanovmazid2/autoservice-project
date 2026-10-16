import csv
import sqlite3
import pytest
from database import (init_database, add_client, update_client, list_clients, delete_client,
                      add_car, list_cars, update_car, delete_car, add_service, list_services,
                      update_service, delete_service, create_order, add_service_to_order,
                      order_details, list_orders, popular_services, active_clients, service_stats,
                      set_order_status)
from reports import export_orders_csv, export_services_txt, backup_database
from seed import seed


@pytest.fixture
def db(tmp_path):
    path = tmp_path / 'test.db'
    init_database(path)
    return path


def test_full_workflow(db, tmp_path):
    client = add_client('Андрей Ким', '+79001112233', db_path=db)
    assert update_client(client, 'Андрей Кимов', '+79001112234', db) == 1
    assert list_clients(db)[0]['full_name'] == 'Андрей Кимов'
    car = add_car(client, 'Mazda', '3', 2018, 'Т111ТТ77', db)
    assert update_car(car, 'Mazda', '6', 2019, db) == 1
    assert list_cars(db)[0]['model'] == '6'
    service = add_service('Полировка', 5000, db)
    assert update_service(service, 'Полировка кузова', 5500, db) == 1
    assert list_services(db)[0]['base_price'] == 5500
    order = create_order(car, db_path=db)
    add_service_to_order(order, service, 2, db)
    add_service_to_order(order, service, 1, db)
    assert order_details(order, db)[0]['amount'] == 16500
    assert list_orders(db)[0]['total'] == 16500
    assert popular_services(db)[0]['uses'] == 3
    assert active_clients(db)[0]['orders_count'] == 1
    assert service_stats(db)['total_value'] == 16500
    assert set_order_status(order, 'выдан', db) == 1
    with pytest.raises(ValueError):
        add_service_to_order(order, service, 1, db)
    csv_path = tmp_path / 'orders.csv'
    txt_path = tmp_path / 'report.txt'
    bak_path = tmp_path / 'backup.db'
    export_orders_csv(csv_path, db)
    export_services_txt(txt_path, db)
    backup_database(bak_path, db)
    with open(csv_path, encoding='utf-8-sig', newline='') as f:
        assert next(csv.DictReader(f))['total'] == '16500.0'
    assert 'Полировка кузова' in txt_path.read_text(encoding='utf-8')
    with sqlite3.connect(bak_path) as conn:
        assert conn.execute('SELECT COUNT(*) FROM orders').fetchone()[0] == 1
    with pytest.raises(sqlite3.IntegrityError):
        delete_service(service, db)
    with pytest.raises(sqlite3.IntegrityError):
        delete_car(car, db)


def test_delete_unused_records(db):
    client = add_client('Пустой Клиент', '+79001234567', db_path=db)
    service = add_service('Мойка', 500, db)
    assert delete_service(service, db) == 1
    assert delete_client(client, db) == 1
    assert delete_client(client, db) == 0
    assert delete_car(999, db) == 0


def test_order_errors(db):
    with pytest.raises(ValueError, match='Заказ не найден'):
        add_service_to_order(999, 999, db_path=db)
    client = add_client('Тест Клиент', '+79001234567', db_path=db)
    car = add_car(client, 'Audi', 'A4', 2017, 'Х111ХХ77', db)
    order = create_order(car, db_path=db)
    with pytest.raises(ValueError, match='Услуга не найдена'):
        add_service_to_order(order, 999, db_path=db)
    assert set_order_status(999, 'готов', db) == 0


def test_seed_idempotent(db):
    assert seed(db) is True
    assert seed(db) is False
    assert service_stats(db)['orders'] == 3
    assert service_stats(db)['completed'] == 1
