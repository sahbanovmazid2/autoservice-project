from database import init_database
from clients import list_clients, add_client
from cars import list_cars, add_car, search_cars
from services import list_services, popular_services
from orders import list_orders, create_order
from statistics import service_stats
from reports import export_orders_csv, export_services_txt, backup_database

def main():
    init_database()
    actions = {
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
    while True:
      print('\nАВТОСЕРВИС | 1 Клиенты | 2 Автомобили | 3 Услуги | 4 Заказы | 5 Добавить клиента | 6 Добавить авто | 7 Создать заказ | 8 Поиск | 9 Популярные услуги | 10 Статистика | 11 CSV | 12 TXT | 13 Резервная копия | 0 Выход')
      choice = input('Пункт: ').strip()
      if choice == '0': break
      try:
        actions.get(choice, lambda: print('Нет такого пункта'))()
      except (ValueError, TypeError) as exc:
        print('Ошибка ввода:', exc)

if __name__ == '__main__':
    main()
