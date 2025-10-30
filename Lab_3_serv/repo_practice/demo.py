import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.services.repo_service import repository_service


def demonstrate_repository():
    print("Патерн Репозиторій\n")

    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        print("АВТОМОБІЛІ")

        new_car = repository_service.create_car(
            make="Toyota",
            model="Camry",
            year=2023,
            price=25000.00,
            in_stock=True
        )
        print(f"Створено новий автомобіль: {new_car}")

        all_cars = repository_service.get_all_cars()
        print(f"Всього автомобілів у БД: {len(all_cars)}")
        for car in all_cars[:5]:
            print(f"  - {car.make} {car.model} {car.year} - ${car.price}")

        print("\nКЛІЄНТИ")

        new_customer = repository_service.create_customer(
            first_name="Іван",
            last_name="Петренко",
            email="ivan@example.com",
            phone="+380501234567"
        )
        print(f"Створено нового клієнта: {new_customer}")

        all_customers = repository_service.get_all_customers()
        print(f"Всього клієнтів у БД: {len(all_customers)}")

        print("\nПРАЦІВНИКИ")

        new_employee = repository_service.create_employee(
            first_name="Марія",
            last_name="Іваненко",
            position="Менеджер з продажів",
            hire_date="2023-01-15"
        )
        print(f"Створено нового працівника: {new_employee}")

        all_employees = repository_service.get_all_employees()
        print(f"Всього працівників у БД: {len(all_employees)}")

        print("\nПОШУК ПО ID")
        car_by_id = repository_service.get_car_by_id(1)
        if car_by_id:
            print(f"Знайдено автомобіль по ID 1: {car_by_id}")
        else:
            print("Автомобіль з ID 1 не знайдено")

        print("\nДОСТУПНІ АВТОМОБІЛІ")
        available_cars = repository_service.get_available_cars()
        print(f"Доступних автомобілів: {len(available_cars)}")

        print("\nДемонстрація успішно завершена")

    except Exception as e:
        print(f"Помилка під час демонстрації: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demonstrate_repository()