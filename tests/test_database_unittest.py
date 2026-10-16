import tempfile
import unittest
from pathlib import Path
from database import (init_database, add_client, add_car, add_service,
                      create_order, add_service_to_order, list_orders,
                      search_cars, delete_client, set_order_status)


class TestAutoService(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'test.db'
        init_database(self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_add_client_and_car(self):
        client = add_client('Иван Петров', '+79001112233', db_path=self.db)
        add_car(client, 'Ford', 'Focus', 2018, 'А001АА77', self.db)
        self.assertEqual(len(search_cars('Ford', self.db)), 1)

    def test_order_total(self):
        client = add_client('Анна Орлова', '+79002223344', db_path=self.db)
        car = add_car(client, 'Honda', 'Civic', 2016, 'В002ВВ77', self.db)
        service = add_service('Замена фильтра', 1500, self.db)
        order = create_order(car, db_path=self.db)
        add_service_to_order(order, service, 2, self.db)
        self.assertEqual(list_orders(self.db)[0]['total'], 3000)

    def test_foreign_key_protection(self):
        client = add_client('Пётр Смирнов', '+79003334455', db_path=self.db)
        add_car(client, 'Skoda', 'Rapid', 2019, 'Е003ЕЕ77', self.db)
        with self.assertRaises(Exception):
            delete_client(client, self.db)

    def test_status_progression(self):
        client = add_client('Мария Соколова', '+79004445566', db_path=self.db)
        car = add_car(client, 'Opel', 'Astra', 2015, 'К004КК77', self.db)
        order = create_order(car, db_path=self.db)
        set_order_status(order, 'готов', self.db)
        with self.assertRaises(ValueError):
            set_order_status(order, 'новый', self.db)


if __name__ == '__main__':
    unittest.main()
