"""Заполнение базы демонстрационными данными."""
from database import (init_database, add_client, add_car, add_service,
                      create_order, add_service_to_order, set_order_status, list_clients)


def seed(db_path=None):
    init_database(db_path)
    if list_clients(db_path):
        return False
    a = add_client('Соколов Артём', '+79001234567', db_path=db_path)
    b = add_client('Морозова Елена', '+79007654321', db_path=db_path)
    c = add_client('Кузнецов Павел', '+79005553322', db_path=db_path)
    car1 = add_car(a, 'Toyota', 'Corolla', 2017, 'А123ВС77', db_path)
    car2 = add_car(b, 'Kia', 'Rio', 2020, 'М456КР77', db_path)
    car3 = add_car(c, 'Lada', 'Vesta', 2022, 'О789ТТ77', db_path)
    oil = add_service('Замена масла', 2500, db_path)
    diag = add_service('Компьютерная диагностика', 1800, db_path)
    brakes = add_service('Замена тормозных колодок', 4200, db_path)
    add_service('Шиномонтаж', 3000, db_path)
    o1 = create_order(car1, 'Плановое ТО', db_path)
    add_service_to_order(o1, oil, db_path=db_path)
    add_service_to_order(o1, diag, db_path=db_path)
    set_order_status(o1, 'выдан', db_path)
    o2 = create_order(car2, 'Скрип тормозов', db_path)
    add_service_to_order(o2, brakes, db_path=db_path)
    set_order_status(o2, 'в работе', db_path)
    o3 = create_order(car3, 'Проверка электроники', db_path)
    add_service_to_order(o3, diag, db_path=db_path)
    return True


if __name__ == '__main__':
    seed()
    print('Демонстрационные данные готовы')
