# файл з бізнес-логікою для операцій buy/sell/modify car.

from typing import Optional, Dict
from .NetworkHelper import NetworkHelper
import logging

logger = logging.getLogger(__name__)


class CarDealerService:
    def __init__(self):
        self.api = NetworkHelper()

    def get_all_cars(self) -> list:
        """Отримати всі машини через API"""
        return self.api.get_list()

    def get_car_by_id(self, car_id: int) -> Optional[Dict]:
        """Отримати машину по ID через API"""
        return self.api.get_by_id(car_id)

    def buy_car(self, car_id: int, dealer_id: int = 1) -> tuple[bool, str]:
        # 1. Отримати дані машини
        car = self.api.get_by_id(car_id)
        if not car:
            return False, "Машину не знайдено"

        # 2. Отримати профіль дилера
        dealer_profile = self.api.get_dealer_profile(dealer_id)
        if not dealer_profile:
            return False, "Профіль дилера не знайдено"

        # 3. Перевірити баланс
        car_price = float(car['price'])
        dealer_balance = float(dealer_profile['balance'])

        if dealer_balance < car_price:
            return False, f"Недостатньо коштів. Потрібно: ${car_price}, Є: ${dealer_balance}"

        # 4. Оновити баланс дилера (віднімаємо ціну)
        new_balance = dealer_balance - car_price
        dealer_update = {
            'name': dealer_profile['name'],
            'balance': new_balance
        }

        updated_dealer = self.api.update_dealer_profile(dealer_id, dealer_update)
        if not updated_dealer:
            return False, "Помилка при оновленні балансу дилера"

        # 5. Змінити owner машини на дилера
        car_update = {
            'brand': car['brand'],
            'model': car['model'],
            'year': car['year'],
            'price': car['price'],
            'owner': dealer_id  # Змінюємо власника
        }

        updated_car = self.api.update_item(car_id, car_update)
        if not updated_car:
            # Відкотити баланс назад
            self.api.update_dealer_profile(dealer_id, {
                'name': dealer_profile['name'],
                'balance': dealer_balance
            })
            return False, "Помилка при оновленні власника машини"

        # 6. Створити транзакцію
        transaction_data = {
            'car': car_id,
            'dealer_profile': dealer_id,
            'transaction_type': 'buy',
            'amount': car_price
        }

        transaction = self.api.create_transaction(transaction_data)
        if not transaction:
            logger.warning(f"Транзакція не створена для car_id={car_id}")

        return True, f"Машину {car['brand']} {car['model']} успішно куплено за ${car_price}"


    def sell_car(self, car_id: int, dealer_id: int = 1) -> tuple[bool, str]:
        # 1. Отримати дані машини
        car = self.api.get_by_id(car_id)
        if not car:
            return False, "Машину не знайдено"

        # 2. Перевірити що машина належить дилеру
        if car.get('owner') != dealer_id:
            return False, "Ця машина не належить вам"

        # 3. Отримати профіль дилера
        dealer_profile = self.api.get_dealer_profile(dealer_id)
        if not dealer_profile:
            return False, "Профіль дилера не знайдено"

        # 4. Оновити баланс дилера (додаємо ціну)
        car_price = float(car['price'])
        dealer_balance = float(dealer_profile['balance'])
        new_balance = dealer_balance + car_price

        dealer_update = {
            'name': dealer_profile['name'],
            'balance': new_balance
        }

        updated_dealer = self.api.update_dealer_profile(dealer_id, dealer_update)
        if not updated_dealer:
            return False, "Помилка при оновленні балансу дилера"

        # 5. Видалити машину
        deleted = self.api.delete_item(car_id)
        if not deleted:
            # Відкотити баланс назад
            self.api.update_dealer_profile(dealer_id, {
                'name': dealer_profile['name'],
                'balance': dealer_balance
            })
            return False, "Помилка при видаленні машини"

        transaction_data = {
            'car': car_id,
            'dealer_profile': dealer_id,
            'transaction_type': 'sell',
            'amount': car_price
        }

        self.api.create_transaction(transaction_data)

        return True, f"Машину {car['brand']} {car['model']} успішно продано за ${car_price}"

    def modify_car(self, car_id: int, new_price: float, dealer_id: int = 1) -> tuple[bool, str]:

        # 1. Отримати дані машини
        car = self.api.get_by_id(car_id)
        if not car:
            return False, "Машину не знайдено"

        # 2. Перевірити що машина належить дилеру
        if car.get('owner') != dealer_id:
            return False, "Ця машина не належить вам"

        # 3. Оновити ціну
        car_update = {
            'brand': car['brand'],
            'model': car['model'],
            'year': car['year'],
            'price': new_price,
            'owner': car['owner']
        }

        updated_car = self.api.update_item(car_id, car_update)
        if not updated_car:
            return False, "Помилка при оновленні машини"

        return True, f"Ціну змінено з ${car['price']} на ${new_price}"

    def get_transaction_history(self, dealer_id: int = 1) -> list:
        """Отримати історію транзакцій дилера"""
        all_transactions = self.api.get_transactions()
        # Фільтруємо тільки транзакції цього дилера
        return [t for t in all_transactions if t.get('dealer_profile') == dealer_id]

    def get_dealer_profile(self, dealer_id: int = 1) -> Optional[Dict]:
        """Отримати профіль дилера"""
        return self.api.get_dealer_profile(dealer_id)
