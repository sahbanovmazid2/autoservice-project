"""Меню автосервиса с авторизацией и разграничением прав."""
from getpass import getpass
from database import init_database
from auth import login
from clients import list_clients, add_client
from cars import list_cars, add_car, search_cars
from services import list_services, popular_services
from orders import list_orders, create_order
from statistics import service_stats
from reports import export_orders_csv, export_services_txt, backup_database


def admin_actions():
    return {
        '1': lambda: print(*list_clients(), sep='\n'),
        '2': lambda: print(*list_cars(), sep='\n'),
        '3': lambda: print(*list_services(), sep='\n'),
        '4': lambda: print(*list_orders(), sep='\n'),
        '5': lambda: print('ID:', add_client(input('Клиент: '), input('Телефон: '))),
        '6': lambda: print('ID:', add_car(int(input('ID клиента: ')), input('Марка: '), input('Модель: '), int(input('Год: ')), input('Номер: '))),
        '7': lambda: print('ID:', create_order(int(input('ID авто: ')), input('Комментарий: '))),
        '8': lambda: print(*search_cars(input('Поиск авто: ')), sep='\n'),
        '9': lambda: print(*popular_services(), sep='\n'),
        '10': lambda: print(service_stats()),
        '11': lambda: print(export_orders_csv()),
        '12': lambda: print(export_services_txt()),
        '13': lambda: print(backup_database()),
    }


def client_actions():
    return {
        '1': lambda: print(*list_services(), sep='\n'),
        '2': lambda: print(*popular_services(), sep='\n'),
    }


def main():
    init_database()
    print('ВХОД В СИСТЕМУ «АВТОСЕРВИС»')
    username = input('Логин: ').strip()
    password = getpass('Пароль: ')
    account = login(username, password)
    if account is None:
        print('Неверный логин или пароль. Доступ запрещён.')
        return
    role = account['role']
    if role not in ('admin', 'user'):
        print('Неизвестная роль. Доступ запрещён.')
        return
    print(f"Вход выполнен: {account['username']}. Роль: {role}")
    actions = admin_actions() if role == 'admin' else client_actions()
    while True:
        if role == 'admin':
            print('\nАДМИНИСТРАТОР | 1 Клиенты | 2 Автомобили | 3 Услуги | 4 Заказы | 5 Добавить клиента | 6 Добавить авто | 7 Создать заказ | 8 Поиск | 9 Популярные услуги | 10 Статистика | 11 CSV | 12 TXT | 13 Резервная копия | 0 Выход')
        else:
            print('\nКЛИЕНТ | 1 Каталог услуг | 2 Популярные услуги | 0 Выход')
        choice = input('Пункт: ').strip()
        if choice == '0':
            break
        if choice not in actions:
            print('Нет доступа к этой операции или такого пункта нет.')
            continue
        try:
            actions[choice]()
        except (ValueError, TypeError) as exc:
            print('Ошибка ввода:', exc)


if __name__ == '__main__':
    main()
