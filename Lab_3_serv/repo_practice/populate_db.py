import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.models import Car, Customer, Employee, Sale
from decimal import Decimal
from datetime import date, timedelta

def add_cars():
    cars = [
        {'make': 'BMW', 'model': 'M5 Competition', 'year': 2024, 'price': Decimal('115000.00'), 'in_stock': True},
        {'make': 'BMW', 'model': 'X7 M60i', 'year': 2024, 'price': Decimal('105000.00'), 'in_stock': True},
        {'make': 'BMW', 'model': '3 Series 330i', 'year': 2023, 'price': Decimal('45000.00'), 'in_stock': True},
        {'make': 'BMW', 'model': 'iX xDrive50', 'year': 2024, 'price': Decimal('87000.00'), 'in_stock': True},
        {'make': 'Porsche', 'model': '911 Turbo S', 'year': 2024, 'price': Decimal('230000.00'), 'in_stock': True},
        {'make': 'Porsche', 'model': 'Cayenne Turbo', 'year': 2024, 'price': Decimal('135000.00'), 'in_stock': True},
        {'make': 'Porsche', 'model': 'Taycan 4S', 'year': 2023, 'price': Decimal('105000.00'), 'in_stock': True},
        {'make': 'Porsche', 'model': 'Macan GTS', 'year': 2024, 'price': Decimal('75000.00'), 'in_stock': True},
        {'make': 'Mercedes-Benz', 'model': 'AMG GT', 'year': 2024, 'price': Decimal('142000.00'), 'in_stock': True},
        {'make': 'Mercedes-Benz', 'model': 'S-Class', 'year': 2023, 'price': Decimal('112000.00'), 'in_stock': True},
    ]

    for car in cars:
        obj, created = Car.objects.get_or_create(
            make=car['make'],
            model=car['model'],
            defaults=car
        )
        if created:
            print(f"Added: {car['make']} {car['model']}")

def add_customers():
    customers = [
        {'first_name': 'Олександр', 'last_name': 'Петренко', 'email': 'petrenko@gmail.com', 'phone': '+380671234567'},
        {'first_name': 'Марія', 'last_name': 'Коваленко', 'email': 'kovalenko@gmail.com', 'phone': '+380672345678'},
        {'first_name': 'Іван', 'last_name': 'Шевченко', 'email': 'shevchenko@gmail.com', 'phone': '+380673456789'},
    ]

    for customer in customers:
        obj, created = Customer.objects.get_or_create(
            email=customer['email'],
            defaults=customer
        )
        if created:
            print(f"Added customer: {customer['first_name']} {customer['last_name']}")

def add_employees():
    employees = [
        {'first_name': 'Андрій', 'last_name': 'Мельник', 'position': 'Менеджер з продажу', 'hire_date': '2022-01-15'},
        {'first_name': 'Наталія', 'last_name': 'Сидоренко', 'position': 'Старший консультант', 'hire_date': '2021-06-10'},
    ]

    for employee in employees:
        obj, created = Employee.objects.get_or_create(
            first_name=employee['first_name'],
            last_name=employee['last_name'],
            defaults=employee
        )
        if created:
            print(f"Added employee: {employee['first_name']} {employee['last_name']}")

def add_sales():
    """Створює тестові продажі для дашборда"""
    print("\n=== Створення тестових продажів ===")
    
    # Отримуємо всіх клієнтів, співробітників та авто
    customers = list(Customer.objects.all())
    employees = list(Employee.objects.all())
    cars = list(Car.objects.filter(in_stock=True))
    
    if not customers:
        print("❌ Немає клієнтів! Спочатку додайте клієнтів.")
        return
    if not employees:
        print("❌ Немає співробітників! Спочатку додайте співробітників.")
        return
    if not cars:
        print("❌ Немає авто! Спочатку додайте авто.")
        return
    
    print(f"📊 Доступно: {len(customers)} клієнтів, {len(employees)} співробітників, {len(cars)} авто")
    
    # Створюємо продажі (безпечно, з перевіркою індексів)
    sales_data = []
    
    # Створюємо декілька продажів, використовуючи циклічний доступ до клієнтів
    num_sales = min(5, len(cars))  # Створимо до 5 продажів
    
    for i in range(num_sales):
        if i < len(cars):
            sales_data.append({
                'car': cars[i],
                'customer': customers[i % len(customers)],  # Циклічно використовуємо клієнтів
                'employee': employees[i % len(employees)],  # Циклічно використовуємо співробітників
                'sale_date': date.today() - timedelta(days=10 - i * 2)
            })
    
    created_count = 0
    for sale_info in sales_data:
        car = sale_info['car']
        # Перевіряємо чи це авто вже продане
        if Sale.objects.filter(car=car).exists():
            print(f"⏭️  Пропускаємо: {car.make} {car.model} вже продано")
            continue

        sale = Sale.objects.create(
            car=car,
            customer=sale_info['customer'],
            employee=sale_info['employee'],
            sale_price=car.price,  # Ціна продажу = ціна авто
            sale_date=sale_info['sale_date']
        )
        created_count += 1
        print(f"✅ Створено продаж: {car.make} {car.model} → {sale_info['customer'].first_name} {sale_info['customer'].last_name} (через {sale_info['employee'].first_name} {sale_info['employee'].last_name})")

    print(f"\n✨ Створено {created_count} нових продажів")

if __name__ == '__main__':
    print("=" * 70)
    print("ЗАПОВНЕННЯ БАЗИ ДАНИХ ТЕСТОВИМИ ДАНИМИ")
    print("=" * 70)

    print()
    add_sales()  # Додаємо продажі

    print("\n" + "=" * 70)
    print("✅ База даних заповнена!")
    print("=" * 70)
    print("\n💡 Тепер відкрийте dashboard: http://127.0.0.1:8000/dashboard/plotly/")

