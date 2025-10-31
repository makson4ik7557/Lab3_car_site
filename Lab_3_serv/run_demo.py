import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')

import django
django.setup()

from repo_practice.services.repo_service import repository_service


def demonstrate():
    print("Автомобілі BMW:")
    bmw_cars = repository_service.cars.get(make__iexact='BMW')
    for car in bmw_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\nАвтомобілі Porsche:")
    porsche_cars = repository_service.cars.get(make__iexact='Porsche')
    for car in porsche_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\nПреміум автомобілі:")
    premium = repository_service.cars.get(price__gte=80000)
    for car in premium:
        print(f"{car.make} {car.model} - ${car.price}")

    print("\nНайдорожчий автомобіль:")
    expensive = repository_service.cars.get_most_expensive()
    if expensive:
        print(f"{expensive.make} {expensive.model} - ${expensive.price}")

    print("\nНайдешевший автомобіль:")
    cheapest = repository_service.cars.get_cheapest()
    if cheapest:
        print(f"{cheapest.make} {cheapest.model} - ${cheapest.price}")

    print("\nКлієнти:")
    customers = repository_service.customers.get()
    for customer in customers:
        print(f"{customer.first_name} {customer.last_name} - {customer.email}")

    print("\nПрацівники:")
    employees = repository_service.employees.get()
    for emp in employees:
        print(f"{emp.first_name} {emp.last_name} - {emp.position}")




if __name__ == '__main__':
    demonstrate()

