"""Экспорт отчётов и резервное копирование базы."""
import csv
import sqlite3
from pathlib import Path
from contextlib import closing
from database import DB_PATH, list_orders, popular_services, service_stats


def export_orders_csv(path='orders.csv', db_path=None):
    rows = list_orders(db_path)
    with open(path, 'w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=['id','opened_at','status','comment','plate','brand','model','client','total'])
        writer.writeheader()
        writer.writerows(rows)
    return str(path)


def export_services_txt(path='services_report.txt', db_path=None):
    with open(path, 'w', encoding='utf-8') as file:
        file.write('ОТЧЁТ ПО УСЛУГАМ АВТОСЕРВИСА\n')
        for row in popular_services(db_path):
            file.write(f"{row['name']}: {row['uses']} шт., {row['revenue']:.2f} руб.\n")
        file.write(f'\nОбщая статистика: {service_stats(db_path)}\n')
    return str(path)


def backup_database(path='autoservice_backup.db', db_path=None):
    source = Path(db_path or DB_PATH)
    target = Path(path)
    if source.resolve() == target.resolve():
        raise ValueError('Резервная копия должна иметь другое имя')
    with closing(sqlite3.connect(str(source))) as src, closing(sqlite3.connect(str(target))) as dst:
        src.backup(dst)
    return str(path)
