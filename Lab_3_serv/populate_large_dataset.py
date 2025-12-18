"""
Скрипт для створення великого набору даних (500+ машин)
Запуск: python populate_large_dataset.py
"""
import os
import django
import sys

# Налаштовуємо Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.models import Car, Customer, Employee, Sale, DealerProfile, Transaction
from django.contrib.auth.models import User
from decimal import Decimal
import random
from datetime import datetime, timedelta


def clear_database():
    """
    Очищає базу даних перед створенням нових даних
    """
    print("\n🗑️  Очищення бази даних...")

    # Видаляємо в правильному порядку (з урахуванням foreign keys)
    Transaction.objects.all().delete()
    print("   ✓ Транзакції видалено")

    Sale.objects.all().delete()
    print("   ✓ Продажі видалено")

    DealerProfile.objects.all().delete()
    print("   ✓ Профілі дилерів видалено")

    # Видаляємо користувачів-дилерів (окрім суперюзерів)
    User.objects.filter(dealer_profile__isnull=True, is_superuser=False).delete()
    print("   ✓ Користувачі-дилери видалено")

    Employee.objects.all().delete()
    print("   ✓ Співробітники видалено")

    Customer.objects.all().delete()
    print("   ✓ Клієнти видалено")

    Car.objects.all().delete()
    print("   ✓ Автомобілі видалено")

    print("✅ База даних очищена!\n")


def create_large_dataset():
    """
    Створює великий набір даних для тестування графіків:
    - 500+ різних автомобілів
    - 200 клієнтів
    - 50 співробітників
    - 1000+ продажів
    - 20 дилерів
    - 500+ транзакцій
    """
    print("=" * 60)
    print("СТВОРЕННЯ ВЕЛИКОГО НАБОРУ ДАНИХ")
    print("=" * 60)

    # Очищаємо базу даних перед створенням нових даних
    clear_database()

    # === 1. СТВОРЕННЯ 500+ АВТОМОБІЛІВ ===
    print("\n📦 Створення автомобілів...")

    makes = [
        'Toyota', 'Honda', 'BMW', 'Mercedes-Benz', 'Audi', 'Ford',
        'Chevrolet', 'Nissan', 'Hyundai', 'Kia', 'Mazda', 'Volkswagen',
        'Porsche', 'Tesla', 'Lexus', 'Subaru', 'Volvo', 'Jaguar',
        'Land Rover', 'Infiniti', 'Acura', 'Cadillac', 'Lincoln'
    ]

    models = [
        'Sedan', 'SUV', 'Truck', 'Coupe', 'Hatchback', 'Convertible',
        'Van', 'Wagon', 'Crossover', 'Sport', 'Luxury', 'Electric',
        'Hybrid', 'Compact', 'Midsize', 'Fullsize'
    ]

    cars = []
    for i in range(550):  # 550 машин
        make = random.choice(makes)
        model = random.choice(models)
        year = random.randint(2010, 2025)
        # Різні цінові категорії
        if make in ['BMW', 'Mercedes-Benz', 'Audi', 'Porsche', 'Tesla', 'Lexus']:
            price = Decimal(random.randint(40000, 120000))
        elif make in ['Toyota', 'Honda', 'Mazda', 'Hyundai', 'Kia']:
            price = Decimal(random.randint(18000, 45000))
        else:
            price = Decimal(random.randint(25000, 75000))

        car = Car(
            make=make,
            model=f'{model} {i + 1}',
            year=year,
            price=price,
            in_stock=random.choice([True, True, True, False])  # 75% в наявності
        )
        cars.append(car)

    Car.objects.bulk_create(cars, ignore_conflicts=True)
    print(f"✅ Створено {len(cars)} автомобілів")

    # === 2. СТВОРЕННЯ 200 КЛІЄНТІВ ===
    print("\n👥 Створення клієнтів...")

    first_names = ['John', 'Mary', 'David', 'Sarah', 'Michael', 'Emma', 'Robert', 'Jessica',
                   'William', 'Lisa', 'James', 'Ashley', 'Daniel', 'Emily', 'Matthew', 'Amanda']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
                  'Rodriguez', 'Martinez', 'Anderson', 'Taylor', 'Thomas', 'Lee', 'White']

    customers = []
    for i in range(200):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=f'{first_name.lower()}.{last_name.lower()}{i}@example.com',
            phone=f'+380{random.randint(100000000, 999999999)}'
        )
        customers.append(customer)

    Customer.objects.bulk_create(customers, ignore_conflicts=True)
    print(f"✅ Створено {len(customers)} клієнтів")

    # === 3. СТВОРЕННЯ 50 СПІВРОБІТНИКІВ ===
    print("\n💼 Створення співробітників...")

    positions = ['Sales Manager', 'Senior Sales', 'Junior Sales', 'Sales Associate',
                'Sales Director', 'Account Manager']

    employees = []
    for i in range(50):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            position=random.choice(positions),
            hire_date=datetime.now().date() - timedelta(days=random.randint(30, 3650))
        )
        employees.append(employee)

    Employee.objects.bulk_create(employees, ignore_conflicts=True)
    print(f"✅ Створено {len(employees)} співробітників")

    # === 4. СТВОРЕННЯ 1000+ ПРОДАЖІВ ===
    print("\n💰 Створення продажів...")

    all_cars = list(Car.objects.all())
    all_customers = list(Customer.objects.all())
    all_employees = list(Employee.objects.all())

    if not all_cars or not all_customers or not all_employees:
        print("❌ Помилка: немає даних для створення продажів")
        return

    sales = []
    for i in range(1200):  # 1200 продажів
        car = random.choice(all_cars)
        customer = random.choice(all_customers)
        employee = random.choice(all_employees)

        # Ціна продажу може бути трохи нижче base price
        sale_price = car.price * Decimal(random.uniform(0.85, 0.98))
        sale_date = datetime.now() - timedelta(days=random.randint(0, 730))  # 2 роки історії

        sale = Sale(
            car=car,
            customer=customer,
            employee=employee,
            sale_price=sale_price,
            sale_date=sale_date
        )
        sales.append(sale)

    Sale.objects.bulk_create(sales, ignore_conflicts=True)
    print(f"✅ Створено {len(sales)} продажів")

    # === 5. СТВОРЕННЯ 20 ДИЛЕРІВ ===
    print("\n🏢 Створення дилерів...")

    dealer_names = [
        'AutoMax', 'CarPro', 'EliteAutos', 'PrimeDrive', 'UrbanMotors',
        'SpeedWay', 'LuxuryCars', 'CityAuto', 'MetroVehicles', 'TopGear',
        'FastLane', 'DriveTime', 'AutoHub', 'CarZone', 'MotorCity',
        'RoadKing', 'AutoPalace', 'CarEmpire', 'WheelDeal', 'AutoCraft'
    ]

    dealers = []
    for name in dealer_names:
        # Перевіряємо чи існує користувач
        if not User.objects.filter(username=name.lower()).exists():
            user = User.objects.create_user(
                username=name.lower(),
                email=f'{name.lower()}@dealer.com',
                password='dealer123',
                first_name=name,
                last_name='Dealer'
            )

            # Створюємо профіль дилера
            DealerProfile.objects.create(
                user=user,  # ✅ Виправлено: user замість dealer
                balance=Decimal(random.randint(10000, 500000))
            )
            dealers.append(user)

    print(f"✅ Створено {len(dealers)} дилерів")

    # === 6. СТВОРЕННЯ 500+ ТРАНЗАКЦІЙ ===
    print("\n💳 Створення транзакцій...")

    all_dealers = list(User.objects.filter(dealer_profile__isnull=False))

    if not all_dealers:
        print("⚠️  Немає дилерів для створення транзакцій")
    else:
        transactions = []
        transaction_types = ['BUY', 'SELL', 'MODIFY']

        for i in range(600):  # 600 транзакцій
            dealer = random.choice(all_dealers)
            trans_type = random.choice(transaction_types)

            # Випадкова машина для транзакції
            car = random.choice(all_cars) if trans_type in ['BUY', 'SELL'] else None

            if trans_type == 'BUY':
                amount = Decimal(random.randint(20000, 100000))
            elif trans_type == 'SELL':
                amount = Decimal(random.randint(15000, 80000))
            else:  # MODIFY
                amount = Decimal(random.randint(5000, 50000))

            # Зберігаємо баланс до транзакції
            balance_before = dealer.dealer_profile.balance

            # Оновлюємо баланс
            if trans_type == 'SELL':
                dealer.dealer_profile.balance += amount
            else:
                dealer.dealer_profile.balance -= amount

            balance_after = dealer.dealer_profile.balance

            transaction = Transaction(
                dealer=dealer,
                car=car,  # ✅ Додано машину
                transaction_type=trans_type,
                amount=amount,
                balance_before=balance_before,  # ✅ Додано balance_before
                balance_after=balance_after,
                description=f'{trans_type} transaction #{i+1}'  # Опис
                # created_at буде автоматично встановлено Django (auto_now_add=True)
            )
            transactions.append(transaction)

        Transaction.objects.bulk_create(transactions, ignore_conflicts=True)

        # Зберігаємо оновлені баланси
        for dealer in all_dealers:
            dealer.dealer_profile.save()

        print(f"✅ Створено {len(transactions)} транзакцій")

    # === ПІДСУМОК ===
    print("\n" + "=" * 60)
    print("✅ ЗАВЕРШЕНО! ПІДСУМОК:")
    print("=" * 60)
    print(f"📦 Автомобілів:    {Car.objects.count()}")
    print(f"👥 Клієнтів:       {Customer.objects.count()}")
    print(f"💼 Співробітників: {Employee.objects.count()}")
    print(f"💰 Продажів:       {Sale.objects.count()}")
    print(f"🏢 Дилерів:        {User.objects.filter(dealer_profile__isnull=False).count()}")
    print(f"💳 Транзакцій:     {Transaction.objects.count()}")
    print("=" * 60)

    # Статистика по марках
    print("\n📊 Топ-10 марок автомобілів:")
    from django.db.models import Count
    top_makes = Car.objects.values('make').annotate(count=Count('id')).order_by('-count')[:10]
    for item in top_makes:
        print(f"   {item['make']}: {item['count']} авто")

    print("\n🎉 Дані готові для тестування графіків!")


if __name__ == '__main__':
    try:
        create_large_dataset()
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()

