"""Операции с SQLite для учёта заказов автосервиса."""
import sqlite3
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from validators import (require_text, validate_phone, validate_plate, validate_year,
                        validate_price, validate_quantity, validate_order_status)

DB_PATH = Path(__file__).with_name('autoservice.db')


@contextmanager
def connect(db_path=None):
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database(db_path=None):
    with connect(db_path) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL CHECK(length(trim(full_name)) > 0),
            phone TEXT NOT NULL,
            email TEXT
        );
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE RESTRICT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            production_year INTEGER NOT NULL CHECK(production_year >= 1950),
            plate TEXT NOT NULL UNIQUE
        );
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            base_price REAL NOT NULL CHECK(base_price >= 0)
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL REFERENCES cars(id) ON DELETE RESTRICT,
            opened_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'новый'
                CHECK(status IN ('новый','в работе','готов','выдан')),
            comment TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS order_services (
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL CHECK(unit_price >= 0),
            PRIMARY KEY (order_id, service_id)
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
            client_id INTEGER REFERENCES clients(id)
        );
        CREATE INDEX IF NOT EXISTS idx_cars_client ON cars(client_id);
        CREATE INDEX IF NOT EXISTS idx_orders_car ON orders(car_id);
        ''')
    from auth import ensure_admin
    ensure_admin(db_path)


def _insert(sql, params, db_path=None):
    with connect(db_path) as conn:
        return conn.execute(sql, params).lastrowid


def _rows(sql, params=(), db_path=None):
    with connect(db_path) as conn:
        return [dict(r) for r in conn.execute(sql, params).fetchall()]


def add_client(full_name, phone, email='', db_path=None):
    return _insert('INSERT INTO clients(full_name,phone,email) VALUES(?,?,?)',
                   (require_text(full_name, 'ФИО'), validate_phone(phone), email.strip()), db_path)


def list_clients(db_path=None):
    return _rows('SELECT * FROM clients ORDER BY id', db_path=db_path)


def update_client(client_id, full_name, phone, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('UPDATE clients SET full_name=?, phone=? WHERE id=?',
                            (require_text(full_name), validate_phone(phone), client_id)).rowcount


def delete_client(client_id, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('DELETE FROM clients WHERE id=?', (client_id,)).rowcount


def add_car(client_id, brand, model, production_year, plate, db_path=None):
    return _insert('INSERT INTO cars(client_id,brand,model,production_year,plate) VALUES(?,?,?,?,?)',
                   (client_id, require_text(brand, 'Марка'), require_text(model, 'Модель'),
                    validate_year(production_year), validate_plate(plate)), db_path)


def list_cars(db_path=None):
    return _rows('''SELECT cars.*, clients.full_name AS owner FROM cars
                   JOIN clients ON clients.id=cars.client_id ORDER BY cars.id''', db_path=db_path)


def update_car(car_id, brand, model, production_year, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('UPDATE cars SET brand=?,model=?,production_year=? WHERE id=?',
                            (require_text(brand), require_text(model), validate_year(production_year), car_id)).rowcount


def delete_car(car_id, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('DELETE FROM cars WHERE id=?', (car_id,)).rowcount


def add_service(name, base_price, db_path=None):
    return _insert('INSERT INTO services(name,base_price) VALUES(?,?)',
                   (require_text(name, 'Услуга'), validate_price(base_price)), db_path)


def list_services(db_path=None):
    return _rows('SELECT * FROM services ORDER BY id', db_path=db_path)


def update_service(service_id, name, base_price, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('UPDATE services SET name=?,base_price=? WHERE id=?',
                            (require_text(name), validate_price(base_price), service_id)).rowcount


def delete_service(service_id, db_path=None):
    with connect(db_path) as conn:
        return conn.execute('DELETE FROM services WHERE id=?', (service_id,)).rowcount


def create_order(car_id, comment='', db_path=None):
    return _insert('INSERT INTO orders(car_id,opened_at,comment) VALUES(?,?,?)',
                   (car_id, date.today().isoformat(), comment.strip()), db_path)


def add_service_to_order(order_id, service_id, quantity=1, db_path=None):
    quantity = validate_quantity(quantity)
    with connect(db_path) as conn:
        order = conn.execute('SELECT status FROM orders WHERE id=?', (order_id,)).fetchone()
        if order is None:
            raise ValueError('Заказ не найден')
        if order['status'] == 'выдан':
            raise ValueError('Нельзя менять выданный заказ')
        service = conn.execute('SELECT base_price FROM services WHERE id=?', (service_id,)).fetchone()
        if service is None:
            raise ValueError('Услуга не найдена')
        conn.execute('''INSERT INTO order_services(order_id,service_id,quantity,unit_price)
                        VALUES(?,?,?,?) ON CONFLICT(order_id,service_id)
                        DO UPDATE SET quantity=quantity+excluded.quantity''',
                     (order_id, service_id, quantity, service['base_price']))


def set_order_status(order_id, status, db_path=None):
    status = validate_order_status(status)
    with connect(db_path) as conn:
        current = conn.execute('SELECT status FROM orders WHERE id=?', (order_id,)).fetchone()
        if current is None:
            return 0
        stages = ('новый', 'в работе', 'готов', 'выдан')
        if stages.index(status) < stages.index(current['status']):
            raise ValueError('Нельзя перевести заказ на предыдущий этап')
        return conn.execute('UPDATE orders SET status=? WHERE id=?', (status, order_id)).rowcount


def list_orders(db_path=None):
    return _rows('''SELECT o.id,o.opened_at,o.status,o.comment,c.plate,
                   c.brand,c.model,cl.full_name AS client,
                   COALESCE(SUM(os.quantity*os.unit_price),0) AS total
                   FROM orders o JOIN cars c ON c.id=o.car_id
                   JOIN clients cl ON cl.id=c.client_id
                   LEFT JOIN order_services os ON os.order_id=o.id
                   GROUP BY o.id ORDER BY o.id''', db_path=db_path)


def order_details(order_id, db_path=None):
    return _rows('''SELECT s.name,os.quantity,os.unit_price,
                   ROUND(os.quantity*os.unit_price,2) AS amount
                   FROM order_services os JOIN services s ON s.id=os.service_id
                   WHERE os.order_id=? ORDER BY s.name''', (order_id,), db_path)


def search_cars(text, db_path=None):
    return _rows('''SELECT c.*,cl.full_name AS owner FROM cars c
                   JOIN clients cl ON cl.id=c.client_id
                   WHERE c.brand LIKE ? OR c.model LIKE ? OR c.plate LIKE ?
                   ORDER BY c.id''', tuple('%'+text+'%' for _ in range(3)), db_path)


def popular_services(db_path=None):
    return _rows('''SELECT s.name,COALESCE(SUM(os.quantity),0) AS uses,
                   COALESCE(ROUND(SUM(os.quantity*os.unit_price),2),0) AS revenue
                   FROM services s LEFT JOIN order_services os ON os.service_id=s.id
                   GROUP BY s.id HAVING uses>0 ORDER BY uses DESC,s.name''', db_path=db_path)


def active_clients(db_path=None):
    return _rows('''SELECT cl.full_name,COUNT(o.id) AS orders_count
                   FROM clients cl JOIN cars c ON c.client_id=cl.id
                   JOIN orders o ON o.car_id=c.id
                   GROUP BY cl.id ORDER BY orders_count DESC''', db_path=db_path)


def service_stats(db_path=None):
    with connect(db_path) as conn:
        return dict(conn.execute('''SELECT
            (SELECT COUNT(*) FROM clients) AS clients,
            (SELECT COUNT(*) FROM cars) AS cars,
            (SELECT COUNT(*) FROM services) AS services,
            (SELECT COUNT(*) FROM orders) AS orders,
            (SELECT COUNT(*) FROM orders WHERE status='выдан') AS completed,
            (SELECT COALESCE(ROUND(SUM(quantity*unit_price),2),0) FROM order_services) AS total_value''').fetchone())
