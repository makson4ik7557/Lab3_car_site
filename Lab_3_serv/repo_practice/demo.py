import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.services.repo_service import repository_service


def demonstrate_repository():
    print("=" * 50)
    print("Демонстрація патерну Repository")
    print("=" * 50)

    print("\n--- Автомобілі BMW ---")
    bmw_cars = repository_service.car_repository.get_cars_by_make('BMW')
    for car in bmw_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\n--- Автомобілі Porsche ---")
    porsche_cars = repository_service.car_repository.get_cars_by_make('Porsche')
    for car in porsche_cars:
        print(f"{car.model} ({car.year}) - ${car.price}")

    print("\n--- Преміум автомобілі (>$80000) ---")
    premium = repository_service.car_repository.get_premium_cars()
    for car in premium:
        print(f"{car.make} {car.model} - ${car.price}")

    print("\n--- Найдорожчий автомобіль ---")
    expensive = repository_service.car_repository.get_most_expensive()
    if expensive:
        print(f"{expensive.make} {expensive.model} - ${expensive.price}")

    print("\n--- Найдешевший автомобіль ---")
    cheap = repository_service.car_repository.get_cheapest()
    if cheap:
        print(f"{cheap.make} {cheap.model} - ${cheap.price}")

    print("\n--- Всі клієнти ---")
    customers = repository_service.get_all_customers()
    print(f"Кількість клієнтів: {len(customers)}")
    for customer in customers:
        print(f"{customer.first_name} {customer.last_name} - {customer.email}")

    print("\n--- Всі працівники ---")
    employees = repository_service.get_all_employees()
    print(f"Кількість працівників: {len(employees)}")
    for emp in employees:
        print(f"{emp.first_name} {emp.last_name} - {emp.position}")

    print("\n" + "=" * 50)
    print("Демонстрація завершена")
    print("=" * 50)


if __name__ == '__main__':
    demonstrate_repository()

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