"""Консольное приложение для автосервиса."""
import sqlite3
from database import *
from reports import export_orders_csv, export_services_txt, backup_database


def show(rows):
    if not rows:
        print('Записей нет')
    for row in rows:
        print(' | '.join(f'{k}: {v}' for k, v in row.items()))


def number(label):
    return int(input(label).strip())


def main():
    init_database()
    actions = {
        '1': lambda: show(list_clients()),
        '2': lambda: show(list_cars()),
        '3': lambda: show(list_services()),
        '4': lambda: show(list_orders()),
        '5': lambda: print('ID клиента:', add_client(input('ФИО: '), input('Телефон: '))),
        '6': lambda: print('ID авто:', add_car(number('ID клиента: '), input('Марка: '), input('Модель: '), number('Год: '), input('Госномер: '))),
        '7': lambda: print('ID услуги:', add_service(input('Название услуги: '), float(input('Цена: ')))),
        '8': lambda: print('ID заказа:', create_order(number('ID автомобиля: '), input('Комментарий: '))),
        '9': lambda: add_service_to_order(number('ID заказа: '), number('ID услуги: '), number('Количество: ')),
        '10': lambda: set_order_status(number('ID заказа: '), input('Статус (новый/в работе/готов/выдан): ')),
        '11': lambda: show(search_cars(input('Марка, модель или госномер: '))),
        '12': lambda: show(popular_services()),
        '13': lambda: show(active_clients()),
        '14': lambda: print(service_stats()),
        '15': lambda: print(export_orders_csv()),
        '16': lambda: print(export_services_txt()),
        '17': lambda: print(backup_database()),
        '18': lambda: print('Изменено:', update_client(number('ID клиента: '), input('Новое ФИО: '), input('Телефон: '))),
        '19': lambda: print('Удалено:', delete_client(number('ID клиента: '))),
        '20': lambda: print('Изменено:', update_car(number('ID авто: '), input('Марка: '), input('Модель: '), number('Год: '))),
        '21': lambda: print('Удалено:', delete_car(number('ID авто: '))),
        '22': lambda: print('Изменено:', update_service(number('ID услуги: '), input('Название: '), float(input('Цена: ')))),
        '23': lambda: print('Удалено:', delete_service(number('ID услуги: '))),
    }
    menu = ('1 Клиенты | 2 Авто | 3 Услуги | 4 Заказы\n'
            '5 Добавить клиента | 6 Добавить авто | 7 Добавить услугу\n'
            '8 Создать заказ | 9 Добавить работу в заказ | 10 Изменить статус\n'
            '11 Поиск авто | 12 Популярные услуги | 13 Активные клиенты | 14 Статистика\n'
            '15 CSV | 16 TXT | 17 Резервная копия\n'
            '18 Изменить клиента | 19 Удалить клиента | 20 Изменить авто | 21 Удалить авто\n'
            '22 Изменить услугу | 23 Удалить услугу | 0 Выход')
    while True:
        print('\n=== AUTOSERVICE MANAGER ===\n' + menu)
        command = input('Выбор: ').strip()
        if command == '0':
            print('Работа завершена')
            return
        try:
            action = actions.get(command)
            if action is None:
                print('Нет такого пункта')
            else:
                action()
        except (ValueError, sqlite3.IntegrityError) as error:
            print('Ошибка:', error)


if __name__ == '__main__':
    main()
