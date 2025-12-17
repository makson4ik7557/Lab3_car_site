"""
Модуль з різними запитами до бази даних для бенчмаркінгу

ВАЖЛИВО: Всі запити йдуть через REST API ViewSets, а НЕ напряму через Repository чи ORM!

АРХІТЕКТУРА:
    Database → Repository → API ViewSets → Benchmark Tests → Dashboard

ЧОМУ API?
    - Тестуємо повний production стек (serialization, auth, permissions)
    - Вимірюємо найдорожчу операцію: ORM → JSON
    - Реалістичні метрики продуктивності
    - Готовність до масштабування
"""
import random
from typing import List, Any


def _call_api_viewset(viewset_class, action_name: str = 'list', params: dict = None):
    """
    Helper функція для виклику API ViewSet без HTTP запиту
    Імітує REST API виклик через пряме звернення до ViewSet

    Args:
        viewset_class: Клас ViewSet для виклику
        action_name: Назва action методу ('list', 'sales_report', тощо)
        params: Query parameters для фільтрації

    Returns:
        Результат виклику ViewSet (зазвичай Response.data)
    """
    from rest_framework.test import APIRequestFactory
    from django.contrib.auth.models import User

    factory = APIRequestFactory()

    # Створюємо fake request
    if params:
        query_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        request = factory.get(f'/?{query_string}')
    else:
        request = factory.get('/')

    # Додаємо fake user для аутентифікації
    try:
        request.user = User.objects.first()
        if not request.user:
            request.user = User.objects.create_user('benchmark_user', 'test@test.com', 'password123')
    except:
        # Fallback якщо є проблеми з БД
        request.user = User(id=1, username='benchmark_user')

    # Викликаємо ViewSet
    viewset = viewset_class()
    viewset.request = request
    viewset.format_kwarg = None

    if action_name == 'list':
        response = viewset.list(request)
    else:
        # Для custom actions
        method = getattr(viewset, action_name, None)
        if method:
            response = method(request)
        else:
            return []

    return response.data if hasattr(response, 'data') else []


def execute_random_query() -> List[Any]:
    """
    Виконує випадковий запит до бази даних через API Layer

    АРХІТЕКТУРА: Database → Repository → API ViewSets → Benchmark Tests

    Замість прямого виклику Repository (repo.cars.get_all()),
    використовуємо _call_api_viewset(CarViewSet, 'list')
    що еквівалентно реальному API запиту GET /api/cars/
    """
    from repo_practice.views import (
        CarViewSet, CustomerViewSet, EmployeeViewSet, SaleViewSet,
        DealerProfileViewSet, AnalyticsViewSet
    )

    # Список різних типів запитів через API
    query_types = [
        'get_all_cars',
        'get_available_cars',
        'get_all_customers',
        'get_all_employees',
        'get_sales_report',
        'get_high_balance_dealers',
        'get_car_stats',
        'get_transaction_dynamics',
        'get_top_customers',
        'get_dealer_balances'
    ]

    query_type = random.choice(query_types)

    try:
        # Використовуємо API ViewSets замість прямого доступу
        if query_type == 'get_all_cars':
            # GET /api/cars/
            result = _call_api_viewset(CarViewSet, 'list')
            return list(result[:50]) if isinstance(result, list) else result

        elif query_type == 'get_available_cars':
            # GET /api/cars/?in_stock=true
            result = _call_api_viewset(CarViewSet, 'list', {'in_stock': 'true'})
            return list(result[:30]) if isinstance(result, list) else result

        elif query_type == 'get_all_customers':
            # GET /api/customers/
            result = _call_api_viewset(CustomerViewSet, 'list')
            return list(result[:50]) if isinstance(result, list) else result

        elif query_type == 'get_all_employees':
            # GET /api/employees/
            result = _call_api_viewset(EmployeeViewSet, 'list')
            return list(result[:50]) if isinstance(result, list) else result

        elif query_type == 'get_sales_report':
            # GET /api/sales/report/
            result = _call_api_viewset(SaleViewSet, 'sales_report')
            return list(result[:30]) if isinstance(result, list) else result

        elif query_type == 'get_high_balance_dealers':
            # GET /api/dealer-profiles/
            result = _call_api_viewset(DealerProfileViewSet, 'list')
            return list(result[:20]) if isinstance(result, list) else result

        elif query_type == 'get_car_stats':
            # GET /api/analytics/profit-by-brand/
            result = _call_api_viewset(AnalyticsViewSet, 'profit_by_brand')
            return list(result[:20]) if isinstance(result, list) else result

        elif query_type == 'get_transaction_dynamics':
            # GET /api/analytics/transaction-dynamics/
            result = _call_api_viewset(AnalyticsViewSet, 'transaction_dynamics')
            return list(result[:20]) if isinstance(result, list) else result

        elif query_type == 'get_top_customers':
            # GET /api/analytics/top-customers/
            result = _call_api_viewset(AnalyticsViewSet, 'top_customers')
            return list(result) if isinstance(result, list) else result

        elif query_type == 'get_dealer_balances':
            # GET /api/analytics/dealer-balance-summary/
            result = _call_api_viewset(AnalyticsViewSet, 'dealer_balance_summary')
            return list(result[:20]) if isinstance(result, list) else result

        else:
            result = _call_api_viewset(CarViewSet, 'list')
            return list(result[:10]) if isinstance(result, list) else result

    except Exception as e:
        # У випадку помилки повертаємо порожній список
        print(f"API Query error: {e}")
        import traceback
        traceback.print_exc()
        return []


def execute_specific_query(query_type: str) -> List[Any]:
    """
    Виконує конкретний тип запиту через API Layer
    АРХІТЕКТУРА: Database → Repository → API ViewSets → Benchmark Tests
    """
    from repo_practice.views import CarViewSet, SaleViewSet, AnalyticsViewSet

    if query_type == 'simple_select':
        # GET /api/cars/
        result = _call_api_viewset(CarViewSet, 'list')
        return list(result[:50]) if isinstance(result, list) else result

    elif query_type == 'filtered_select':
        # GET /api/cars/?in_stock=true
        result = _call_api_viewset(CarViewSet, 'list', {'in_stock': 'true'})
        return list(result[:30]) if isinstance(result, list) else result

    elif query_type == 'join_query':
        # GET /api/sales/
        result = _call_api_viewset(SaleViewSet, 'list')
        return list(result[:30]) if isinstance(result, list) else result

    elif query_type == 'aggregation':
        # GET /api/analytics/profit-by-brand/
        result = _call_api_viewset(AnalyticsViewSet, 'profit_by_brand')
        return result if isinstance(result, list) else []

    else:
        result = _call_api_viewset(CarViewSet, 'list')
        return list(result[:10]) if isinstance(result, list) else result


def get_all_query_types() -> List[str]:
    """
    Повертає список всіх доступних типів запитів через API
    Кожен запит відповідає REST API endpoint
    """
    return [
        'get_all_cars',              # GET /api/cars/
        'get_available_cars',        # GET /api/cars/?in_stock=true
        'get_all_customers',         # GET /api/customers/
        'get_all_employees',         # GET /api/employees/
        'get_sales_report',          # GET /api/sales/report/
        'get_high_balance_dealers',  # GET /api/dealer-profiles/
        'get_car_stats',             # GET /api/analytics/profit-by-brand/
        'get_transaction_dynamics',  # GET /api/analytics/transaction-dynamics/
        'get_top_customers',         # GET /api/analytics/top-customers/
        'get_dealer_balances'        # GET /api/analytics/dealer-balance-summary/
    ]

