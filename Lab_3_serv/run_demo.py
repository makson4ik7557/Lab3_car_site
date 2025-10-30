import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')

import django
django.setup()

from repo_practice.services.repo_service import repository_service


def demonstrate():
    print("Автомобілі BMW:")
    bmw_cars = repository_service.car_repository.get_cars_by_make('BMW')
    for car in bmw_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\nАвтомобілі Porsche:")
    porsche_cars = repository_service.car_repository.get_cars_by_make('Porsche')
    for car in porsche_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\nПреміум автомобілі:")
    premium = repository_service.car_repository.get_premium_cars()
    for car in premium:
        print(f"{car.make} {car.model} - ${car.price}")

    print("\nНайдорожчий автомобіль:")
    expensive = repository_service.car_repository.get_most_expensive()
    if expensive:
        print(f"{expensive.make} {expensive.model} - ${expensive.price}")

    print("\nКлієнти:")
    customers = repository_service.get_all_customers()
    for customer in customers:
        print(f"{customer.first_name} {customer.last_name} - {customer.email}")

    print("\nПрацівники:")
    employees = repository_service.get_all_employees()
    for emp in employees:
        print(f"{emp.first_name} {emp.last_name} - {emp.position}")



if __name__ == '__main__':
    demonstrate()

