from typing import List, Dict, Any
from django.db.models import Sum, Avg, Count, Max, Min, Q
from django.db.models.functions import TruncMonth
from ..models import Car, Sale, Transaction


class AnalyticsRepository:
    """
    Репозиторій для агрегованих аналітичних запитів.
    Всі методи використовують складні ORM запити з GROUP BY, HAVING, агрегаціями та сортуванням.
    """

    def get_sales_by_employee(self, min_sales_count: int = 1) -> List[Dict[str, Any]]:
        """
        Агрегований запит 1: Продажі по співробітниках

        Використовує:
        - Кілька сутностей: Sale, Employee
        - GROUP BY: employee
        - Агрегації: SUM, AVG, COUNT
        - HAVING: count >= min_sales_count
        - ORDER BY: total_revenue DESC

        Returns:
            List of dicts with employee info and sales statistics
        """
        return list(
            Sale.objects
            .select_related('employee')
            .values(
                'employee__id',
                'employee__first_name',
                'employee__last_name',
                'employee__position'
            )
            .annotate(
                total_sales=Count('id'),
                total_revenue=Sum('sale_price'),
                average_sale_price=Avg('sale_price'),
                max_sale=Max('sale_price'),
                min_sale=Min('sale_price')
            )
            .filter(total_sales__gte=min_sales_count)  # HAVING clause
            .order_by('-total_revenue')
        )

    def get_profit_by_car_brand(self, min_cars_sold: int = 1) -> List[Dict[str, Any]]:
        """
        Агрегований запит 2: Прибуток по марках автомобілів

        Використовує:
        - Кілька сутностей: Sale, Car
        - GROUP BY: car__make
        - Агрегації: SUM, AVG, COUNT
        - HAVING: cars_sold >= min_cars_sold
        - ORDER BY: total_revenue DESC

        Returns:
            List of dicts with car brand and revenue statistics
        """
        return list(
            Sale.objects
            .select_related('car')
            .values('car__make')
            .annotate(
                cars_sold=Count('id'),
                total_revenue=Sum('sale_price'),
                average_price=Avg('sale_price'),
                highest_sale=Max('sale_price')
            )
            .filter(cars_sold__gte=min_cars_sold)  # HAVING clause
            .order_by('-total_revenue')
        )

    def get_transaction_dynamics_by_dealer(self, min_amount: float = 0) -> List[Dict[str, Any]]:
        """
        Агрегований запит 3: Динаміка транзакцій дилерів по типах

        Використовує:
        - Кілька сутностей: Transaction, User (dealer), DealerProfile
        - GROUP BY: dealer, transaction_type
        - Агрегації: SUM, COUNT, MAX
        - HAVING: total_amount >= min_amount
        - ORDER BY: dealer__username, total_amount DESC

        Returns:
            List of dicts with dealer transaction statistics by type
        """
        return list(
            Transaction.objects
            .select_related('dealer', 'dealer__dealer_profile')
            .values(
                'dealer__id',
                'dealer__username',
                'transaction_type'
            )
            .annotate(
                transaction_count=Count('id'),
                total_amount=Sum('amount'),
                average_amount=Avg('amount'),
                latest_balance=Max('balance_after')
            )
            .filter(total_amount__gte=min_amount)  # HAVING clause
            .order_by('dealer__username', '-total_amount')
        )

    def get_top_customers_by_spending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Агрегований запит 4: Топ клієнтів по витратам

        Використовує:
        - Кілька сутностей: Sale, Customer, Car
        - GROUP BY: customer
        - Агрегації: SUM, COUNT, MAX, AVG
        - ORDER BY: total_spent DESC
        - LIMIT: limit

        Returns:
            List of dicts with top customers and their spending
        """
        return list(
            Sale.objects
            .select_related('customer', 'car')
            .values(
                'customer__id',
                'customer__first_name',
                'customer__last_name',
                'customer__email'
            )
            .annotate(
                cars_purchased=Count('id'),
                total_spent=Sum('sale_price'),
                average_purchase=Avg('sale_price'),
                most_expensive_purchase=Max('sale_price')
            )
            .order_by('-total_spent')[:limit]
        )

    def get_car_price_statistics_by_year(self, min_cars_count: int = 1) -> List[Dict[str, Any]]:
        """
        Агрегований запит 5: Середні ціни та статистика автомобілів по рокам виробництва

        Використовує:
        - Сутність: Car
        - GROUP BY: year
        - Агрегації: AVG, COUNT, MAX, MIN
        - HAVING: cars_count >= min_cars_count
        - ORDER BY: year DESC

        Returns:
            List of dicts with car statistics by manufacturing year
        """
        return list(
            Car.objects
            .values('year')
            .annotate(
                cars_count=Count('id'),
                average_price=Avg('price'),
                max_price=Max('price'),
                min_price=Min('price'),
                in_stock_count=Count('id', filter=Q(in_stock=True))
            )
            .filter(cars_count__gte=min_cars_count)  # HAVING clause
            .order_by('-year')
        )

    def get_dealer_balance_summary(self, min_transactions: int = 1) -> List[Dict[str, Any]]:
        """
        Агрегований запит 6: Сумарна інформація про баланси дилерів з групуванням по типах транзакцій

        Використовує:
        - Кілька сутностей: Transaction, User (dealer), DealerProfile
        - GROUP BY: dealer
        - Агрегації: MAX, COUNT, SUM з різними фільтрами
        - HAVING: total_transactions >= min_transactions
        - ORDER BY: current_balance DESC

        Returns:
            List of dicts with dealer balance and transaction statistics
        """
        return list(
            Transaction.objects
            .select_related('dealer', 'dealer__dealer_profile')
            .values(
                'dealer__id',
                'dealer__username',
            )
            .annotate(
                total_transactions=Count('id'),
                current_balance=Max('balance_after'),
                buy_transactions=Count('id', filter=Q(transaction_type='BUY')),
                sell_transactions=Count('id', filter=Q(transaction_type='SELL')),
                modify_transactions=Count('id', filter=Q(transaction_type='MODIFY')),
                total_buy_amount=Sum('amount', filter=Q(transaction_type='BUY')),
                total_sell_amount=Sum('amount', filter=Q(transaction_type='SELL')),
                average_transaction=Avg('amount')
            )
            .filter(total_transactions__gte=min_transactions)  # HAVING clause
            .order_by('-current_balance')
        )

    def get_monthly_sales_trend(self, year: int = None) -> List[Dict[str, Any]]:
        """
        Додатковий агрегований запит: Тренд продажів по місяцях

        Використовує:
        - Кілька сутностей: Sale, Car, Customer, Employee
        - GROUP BY: month (TruncMonth)
        - Агрегації: COUNT, SUM, AVG
        - Фільтр по року (опціонально)
        - ORDER BY: month

        Returns:
            List of dicts with monthly sales trends
        """
        queryset = Sale.objects.select_related('car', 'customer', 'employee')

        if year:
            queryset = queryset.filter(sale_date__year=year)

        return list(
            queryset
            .annotate(month=TruncMonth('sale_date'))
            .values('month')
            .annotate(
                sales_count=Count('id'),
                total_revenue=Sum('sale_price'),
                average_sale=Avg('sale_price'),
                unique_customers=Count('customer', distinct=True),
                unique_employees=Count('employee', distinct=True)
            )
            .order_by('month')
        )

    def get_car_inventory_by_brand_and_stock(self) -> List[Dict[str, Any]]:
        """
        Додатковий агрегований запит: Інвентаризація автомобілів по марках та статусу наявності

        Використовує:
        - Сутність: Car
        - GROUP BY: make, in_stock
        - Агрегації: COUNT, AVG, SUM
        - ORDER BY: make, in_stock

        Returns:
            List of dicts with inventory statistics
        """
        return list(
            Car.objects
            .values('make', 'in_stock')
            .annotate(
                cars_count=Count('id'),
                average_price=Avg('price'),
                total_value=Sum('price'),
                avg_year=Avg('year')
            )
            .order_by('make', '-in_stock')
        )

