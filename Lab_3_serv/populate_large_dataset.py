"""
Скрипт для заповнення БД великою кількістю тестових даних (200-500 записів)
"""
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Lab_3_serv.settings')
django.setup()

from repo_practice.models import Car, Customer, Employee, Sale, User, DealerProfile, Transaction
from django.contrib.auth.hashers import make_password

# Дані для генерації
CAR_MAKES = {
    'BMW': ['M5 Competition', 'X7 M60i', '3 Series 330i', 'iX xDrive50', '5 Series', 'X5', 'M3', 'M4', 'X3', '7 Series'],
    'Mercedes-Benz': ['AMG GT', 'S-Class', 'E-Class', 'GLE', 'GLC', 'A-Class', 'C-Class', 'G-Class', 'CLS', 'GLA'],
    'Audi': ['RS6', 'Q7', 'A6', 'Q5', 'A4', 'A8', 'Q8', 'e-tron', 'A3', 'RS5'],
    'Porsche': ['911 Turbo S', 'Cayenne Turbo', 'Taycan 4S', 'Macan GTS', 'Panamera', '718 Cayman', 'Boxster', '911 Carrera', 'Cayenne', 'Macan'],
    'Tesla': ['Model S Plaid', 'Model X', 'Model 3', 'Model Y', 'Cybertruck'],
    'Lexus': ['LS 500', 'RX 350', 'ES 300h', 'NX', 'LC 500', 'GX', 'IS', 'UX'],
    'Volvo': ['XC90', 'S90', 'XC60', 'V90', 'XC40', 'S60'],
    'Jaguar': ['F-Type', 'XF', 'XE', 'F-PACE', 'E-PACE', 'I-PACE'],
    'Land Rover': ['Range Rover', 'Defender', 'Discovery', 'Range Rover Sport', 'Evoque'],
    'Maserati': ['Quattroporte', 'Levante', 'Ghibli', 'MC20', 'GranTurismo']
}

FIRST_NAMES = [
    'Олександр', 'Андрій', 'Максим', 'Дмитро', 'Іван', 'Микола', 'Віктор', 'Сергій', 'Володимир', 'Олег',
    'Марія', 'Наталія', 'Олена', 'Ірина', 'Анна', 'Тетяна', 'Юлія', 'Світлана', 'Катерина', 'Вікторія',
    'Богдан', 'Ярослав', 'Артем', 'Денис', 'Роман', 'Євген', 'Павло', 'Петро', 'Василь', 'Михайло'
]

LAST_NAMES = [
    'Петренко', 'Коваленко', 'Шевченко', 'Бойко', 'Коваль', 'Мельник', 'Гончар', 'Кравченко', 'Ткаченко', 'Поліщук',
    'Мороз', 'Савченко', 'Левченко', 'Павленко', 'Сидоренко', 'Захарченко', 'Григоренко', 'Іваненко', 'Марченко', 'Яковенко',
    'Зайцев', 'Білий', 'Руденко', 'Кравець', 'Козлов', 'Гриценко', 'Романенко', 'Литвиненко', 'Данченко', 'Федоренко'
]

POSITIONS = [
    'Менеджер з продажу',
    'Старший консультант',
    'Консультант з продажу',
    'Керівник відділу продажів',
    'Спеціаліст з обслуговування клієнтів',
    'Фінансовий консультант',
    'Головний менеджер',
    'Регіональний менеджер'
]

def clear_existing_data():
    """Очищення існуючих даних (опціонально)"""
    print("\nОчищення старих даних...")
    Sale.objects.all().delete()
    Transaction.objects.filter(dealer__username__startswith='dealer_').delete()
    Car.objects.all().delete()
    Customer.objects.all().delete()
    Employee.objects.all().delete()
    DealerProfile.objects.filter(user__username__startswith='dealer_').delete()
    User.objects.filter(username__startswith='dealer_').delete()
    print("Старі дані очищено")

def create_cars(count=300):
    """Створює автомобілі"""
    print(f"\nСтворення {count} автомобілів...")
    cars = []

    for i in range(count):
        make = random.choice(list(CAR_MAKES.keys()))
        model = random.choice(CAR_MAKES[make])
        year = random.randint(2018, 2024)

        # Ціна залежить від марки та року
        base_prices = {
            'BMW': (45000, 150000),
            'Mercedes-Benz': (50000, 180000),
            'Audi': (40000, 140000),
            'Porsche': (70000, 250000),
            'Tesla': (45000, 130000),
            'Lexus': (45000, 100000),
            'Volvo': (40000, 80000),
            'Jaguar': (50000, 120000),
            'Land Rover': (60000, 150000),
            'Maserati': (80000, 200000)
        }

        min_price, max_price = base_prices[make]
        price = Decimal(random.randint(min_price, max_price))

        # 70% в stock, 30% продані
        in_stock = random.random() < 0.7

        car = Car(
            make=make,
            model=model,
            year=year,
            price=price,
            in_stock=in_stock
        )
        cars.append(car)

    Car.objects.bulk_create(cars)
    print(f"Створено {len(cars)} автомобілів")
    return list(Car.objects.all())

def create_customers(count=150):
    """Створює клієнтів"""
    print(f"\n👥 Створення {count} клієнтів...")
    customers = []

    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
        phone = f"+38067{random.randint(1000000, 9999999)}"

        customer = Customer(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone
        )
        customers.append(customer)

    Customer.objects.bulk_create(customers)
    print(f"Створено {len(customers)} клієнтів")
    return list(Customer.objects.all())

def create_employees(count=15):
    """Створює співробітників"""
    print(f"\nСтворення {count} співробітників...")
    employees = []

    for i in range(count):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        position = random.choice(POSITIONS)
        hire_date = datetime.now().date() - timedelta(days=random.randint(180, 1825))

        employee = Employee(
            first_name=first_name,
            last_name=last_name,
            position=position,
            hire_date=hire_date
        )
        employees.append(employee)

    Employee.objects.bulk_create(employees)
    print(f"Створено {len(employees)} співробітників")
    return list(Employee.objects.all())

def create_dealers(count=5):
    """Створює дилерів"""
    print(f"\nСтворення {count} дилерів...")
    dealers = []

    for i in range(1, count + 1):
        username = f"dealer_{i}"

        # Перевіряємо чи існує
        if User.objects.filter(username=username).exists():
            dealer = User.objects.get(username=username)
        else:
            dealer = User.objects.create(
                username=username,
                email=f"dealer{i}@example.com",
                password=make_password('password123'),
                is_staff=True
            )

        # Створюємо профіль якщо немає
        if not hasattr(dealer, 'dealer_profile'):
            DealerProfile.objects.create(
                user=dealer,
                balance=Decimal(random.randint(50000, 200000))
            )

        dealers.append(dealer)

    print(f"Створено {len(dealers)} дилерів")
    return dealers

def create_sales(cars, customers, employees, count=200):
    """Створює продажі"""
    print(f"\nСтворення {count} продажів...")

    # Беремо тільки продані авто
    sold_cars = [car for car in cars if not car.in_stock]

    if len(sold_cars) < count:
        # Позначаємо додаткові авто як продані
        additional_needed = count - len(sold_cars)
        available_cars = [car for car in cars if car.in_stock][:additional_needed]

        for car in available_cars:
            car.in_stock = False

        Car.objects.bulk_update(available_cars, ['in_stock'])
        sold_cars.extend(available_cars)

    sales = []
    for i in range(min(count, len(sold_cars))):
        car = sold_cars[i]
        customer = random.choice(customers)
        employee = random.choice(employees)

        # Ціна продажу може трохи відрізнятись від базової
        price_variation = Decimal(random.uniform(0.95, 1.05))
        sale_price = car.price * price_variation

        sale = Sale(
            car=car,
            customer=customer,
            employee=employee,
            sale_price=sale_price
        )
        sales.append(sale)

    Sale.objects.bulk_create(sales)
    print(f"Створено {len(sales)} продажів")

def create_transactions(dealers, cars, count=300):
    """Створює транзакції"""
    print(f"\nСтворення {count} транзакцій...")
    transactions = []

    for i in range(count):
        dealer = random.choice(dealers)
        profile = dealer.dealer_profile

        transaction_type = random.choice(['BUY', 'SELL', 'MODIFY'])

        if transaction_type == 'BUY':
            car = random.choice([c for c in cars if c.in_stock])
            amount = -car.price * Decimal(random.uniform(0.8, 0.9))  # Купівля зі знижкою
            description = f"Купівля {car.make} {car.model}"
        elif transaction_type == 'SELL':
            car = random.choice([c for c in cars if not c.in_stock])
            amount = car.price * Decimal(random.uniform(1.0, 1.15))  # Продаж з націнкою
            description = f"Продаж {car.make} {car.model}"
        else:  # MODIFY
            car = random.choice(cars)
            amount = Decimal(random.randint(500, 5000))
            description = f"Модифікація {car.make} {car.model}"

        balance_before = profile.balance
        balance_after = balance_before + amount

        transaction = Transaction(
            dealer=dealer,
            car=car,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            balance_before=balance_before,
            balance_after=balance_after
        )
        transactions.append(transaction)

        # Оновлюємо баланс
        profile.balance = balance_after
        profile.save()

    Transaction.objects.bulk_create(transactions)
    print(f"Створено {len(transactions)} транзакцій")

def main():
    print("ЗАПОВНЕННЯ БД ВЕЛИКОЮ КІЛЬКІСТЮ ДАНИХ")

    # Запитуємо чи очищати старі дані
    response = input("\nОчистити існуючі дані? (y/n): ").lower()
    if response == 'y':
        clear_existing_data()

    # Створюємо дані
    print("\nПочаток генерації даних...")

    cars = create_cars(300)
    customers = create_customers(150)
    employees = create_employees(15)
    dealers = create_dealers(5)

    create_sales(cars, customers, employees, 200)
    create_transactions(dealers, cars, 300)

    print("ЗАПОВНЕННЯ ЗАВЕРШЕНО")

    # Статистика
    print(f"\nПідсумкова статистика:")
    print(f"Автомобілів: {Car.objects.count()}")
    print(f"Клієнтів: {Customer.objects.count()}")
    print(f"Співробітників: {Employee.objects.count()}")
    print(f"Дилерів: {User.objects.filter(username__startswith='dealer_').count()}")
    print(f"Продажів: {Sale.objects.count()}")
    print(f"Транзакцій: {Transaction.objects.count()}")

if __name__ == '__main__':
    main()

