"""
Analytics Service Layer - Бізнес-логіка для аналітики

Відповідальність:
- Отримання даних з Repository
- Обчислення статистики
- Надання даних для Dashboard і REST API
"""
import pandas as pd
import logging
from decimal import Decimal
from typing import Dict, Any, Tuple
from repo_practice.services.repo_service import RepositoryService

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service для аналітичних операцій з pandas"""

    def __init__(self):
        self.repo = RepositoryService()

    def _convert_decimals_to_float(self, df: pd.DataFrame) -> pd.DataFrame:
        """Конвертує Decimal колонки в float для Plotly/Bokeh"""
        for col in df.columns:
            if df[col].dtype == 'object':
                # Перевіряємо чи є Decimal значення
                if len(df) > 0 and isinstance(df[col].iloc[0], Decimal):
                    df[col] = df[col].astype(float)
        return df

    # === АГРЕГОВАНИЙ ЗАПИТ 1: Продажі по співробітниках ===

    def get_sales_by_employee_df(self, min_sales: int = 1) -> pd.DataFrame:
        """
        Повертає DataFrame з продажами по співробітниках

        Returns:
            pd.DataFrame with columns: employee__id, employee__first_name,
            employee__last_name, employee__position, total_sales, total_revenue,
            average_sale_price, max_sale, min_sale
        """
        data = self.repo.analytics.get_sales_by_employee(min_sales)
        df = pd.DataFrame(data)

        if df.empty:
            return df

        # Додаткова обробка
        df = self._convert_decimals_to_float(df)
        df['full_name'] = df['employee__first_name'] + ' ' + df['employee__last_name']

        return df

    def get_sales_statistics(self, min_sales: int = 1) -> Dict[str, Any]:
        """Обчислює статистику для продажів"""
        df = self.get_sales_by_employee_df(min_sales)

        if df.empty:
            return {}

        return {
            'mean_revenue': float(df['total_revenue'].mean()),
            'median_revenue': float(df['total_revenue'].median()),
            'min_revenue': float(df['total_revenue'].min()),
            'max_revenue': float(df['total_revenue'].max()),
            'mean_sales_count': float(df['total_sales'].mean()),
            'total_employees': len(df)
        }

    # === АГРЕГОВАНИЙ ЗАПИТ 2: Прибуток по марках ===

    def get_profit_by_brand_df(self, min_cars: int = 1) -> pd.DataFrame:
        """
        Повертає DataFrame з прибутком по марках автомобілів

        Returns:
            pd.DataFrame with columns: car__make, cars_sold, total_revenue,
            average_price, highest_sale
        """
        data = self.repo.analytics.get_profit_by_car_brand(min_cars)
        df = pd.DataFrame(data)

        if not df.empty:
            df = self._convert_decimals_to_float(df)

        return df

    def get_profit_statistics(self, min_cars: int = 1) -> Dict[str, Any]:
        """Обчислює статистику для прибутку по марках"""
        df = self.get_profit_by_brand_df(min_cars)

        if df.empty:
            return {}

        return {
            'mean_revenue_per_brand': float(df['total_revenue'].mean()),
            'median_revenue_per_brand': float(df['total_revenue'].median()),
            'highest_revenue_brand': df.loc[df['total_revenue'].idxmax()]['car__make'],
            'lowest_revenue_brand': df.loc[df['total_revenue'].idxmin()]['car__make'],
            'total_brands': len(df),
            'total_revenue_all_brands': float(df['total_revenue'].sum())
        }

    # === АГРЕГОВАНИЙ ЗАПИТ 3: Динаміка транзакцій ===

    def get_transaction_dynamics_df(self, min_amount: float = 0) -> pd.DataFrame:
        """
        Повертає DataFrame з динамікою транзакцій дилерів

        Returns:
            pd.DataFrame with columns: dealer__id, dealer__username,
            transaction_type, transaction_count, total_amount,
            average_amount, latest_balance
        """
        data = self.repo.analytics.get_transaction_dynamics_by_dealer(min_amount)
        df = pd.DataFrame(data)

        if not df.empty:
            df = self._convert_decimals_to_float(df)

        return df

    def get_transaction_statistics(self, min_amount: float = 0) -> Dict[str, Any]:
        """Обчислює статистику для транзакцій"""
        df = self.get_transaction_dynamics_df(min_amount)

        if df.empty:
            return {}

        # Групуємо по типу транзакції
        type_stats = df.groupby('transaction_type').agg({
            'total_amount': 'sum',
            'transaction_count': 'sum'
        }).to_dict(orient='index')

        return {
            'total_dealers': df['dealer__username'].nunique(),
            'total_transactions': int(df['transaction_count'].sum()),
            'total_amount': float(df['total_amount'].sum()),
            'by_type': type_stats
        }

    # === АГРЕГОВАНИЙ ЗАПИТ 4: Топ клієнтів ===

    def get_top_customers_df(self, limit: int = 10) -> pd.DataFrame:
        """
        Повертає DataFrame з топ клієнтами по витратам

        Returns:
            pd.DataFrame with columns: customer__id, customer__first_name,
            customer__last_name, customer__email, cars_purchased,
            total_spent, average_purchase, most_expensive_purchase
        """
        data = self.repo.analytics.get_top_customers_by_spending(limit)
        df = pd.DataFrame(data)

        if not df.empty:
            df = self._convert_decimals_to_float(df)
            df['full_name'] = df['customer__first_name'] + ' ' + df['customer__last_name']

        return df

    def get_customers_statistics(self, limit: int = 10) -> Dict[str, Any]:
        """Обчислює статистику для топ клієнтів"""
        df = self.get_top_customers_df(limit)

        if df.empty:
            return {}

        return {
            'total_customers': len(df),
            'total_spent_all': float(df['total_spent'].sum()),
            'average_spent_per_customer': float(df['total_spent'].mean()),
            'total_cars_purchased': int(df['cars_purchased'].sum())
        }

    # === АГРЕГОВАНИЙ ЗАПИТ 5: Статистика цін по рокам ===

    def get_car_price_statistics_df(self, min_cars: int = 1) -> pd.DataFrame:
        """
        Повертає DataFrame зі статистикою цін автомобілів по рокам

        Returns:
            pd.DataFrame with columns: year, cars_count, average_price,
            max_price, min_price, in_stock_count
        """
        data = self.repo.analytics.get_car_price_statistics_by_year(min_cars)
        df = pd.DataFrame(data)

        if not df.empty:
            df = self._convert_decimals_to_float(df)
            df['year_str'] = df['year'].astype(str)

        return df

    def get_car_price_range_statistics(self, min_cars: int = 1) -> Dict[str, Any]:
        """Обчислює статистику цінових діапазонів"""
        df = self.get_car_price_statistics_df(min_cars)

        if df.empty:
            return {}

        return {
            'years_range': f"{df['year'].min()} - {df['year'].max()}",
            'total_cars': int(df['cars_count'].sum()),
            'overall_average_price': float(df['average_price'].mean()),
            'highest_max_price': float(df['max_price'].max()),
            'lowest_min_price': float(df['min_price'].min())
        }

    # === АГРЕГОВАНИЙ ЗАПИТ 6: Баланси дилерів ===

    def get_dealer_balance_summary_df(self, min_transactions: int = 1) -> pd.DataFrame:
        """
        Повертає DataFrame з балансами та операціями дилерів

        Returns:
            pd.DataFrame with columns: dealer__id, dealer__username,
            total_transactions, current_balance, buy_transactions,
            sell_transactions, modify_transactions, total_buy_amount,
            total_sell_amount, average_transaction
        """
        data = self.repo.analytics.get_dealer_balance_summary(min_transactions)
        df = pd.DataFrame(data)

        if not df.empty:
            # Конвертуємо Decimal в float для всіх числових колонок
            numeric_cols = ['current_balance', 'total_buy_amount', 'total_sell_amount', 'average_transaction']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = df[col].fillna(0).astype(float)

        return df

    def get_dealer_balance_statistics(self, min_transactions: int = 1) -> Dict[str, Any]:
        """Обчислює статистику балансів дилерів"""
        df = self.get_dealer_balance_summary_df(min_transactions)

        if df.empty:
            return {}

        return {
            'total_dealers': len(df),
            'mean_balance': float(df['current_balance'].mean()),
            'median_balance': float(df['current_balance'].median()),
            'total_buy_operations': int(df['buy_transactions'].sum()),
            'total_sell_operations': int(df['sell_transactions'].sum()),
            'total_buy_amount': float(df['total_buy_amount'].sum()),
            'total_sell_amount': float(df['total_sell_amount'].sum())
        }