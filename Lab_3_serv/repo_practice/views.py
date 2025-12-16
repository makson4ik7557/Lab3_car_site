from rest_framework import viewsets, status
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomerSerializer, EmployeeSerializer, SaleSerializer, DealerProfileSerializer, TransactionSerializer

from .serializers import CarSerializer
from .services.repo_service import RepositoryService

from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction as db_transaction
from decimal import Decimal
import pandas as pd


class BaseAuthenticatedViewSet(viewsets.ModelViewSet):
    authentication_classes = [BasicAuthentication] #base auth
    permission_classes = [IsAuthenticated] #only authenticated users

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryService()

    def get_object(self):
        pk = self.kwargs.get('pk')
        return self.repo_attribute.get_by_id(pk)

    def perform_create(self, serializer):
        validated_data = serializer.validated_data
        instance = self.repo_attribute.create(**validated_data)
        serializer.instance = instance

    def perform_update(self, serializer):
        pk = self.kwargs.get('pk')
        validated_data = serializer.validated_data
        instance = self.repo_attribute.update(pk, **validated_data)
        serializer.instance = instance

    def perform_destroy(self, instance):
        pk = self.kwargs.get('pk')
        self.repo_attribute.delete(pk)

class CarViewSet(BaseAuthenticatedViewSet):
    serializer_class = CarSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.cars

    def get_queryset(self):
        return self.repo.cars.get_all()

class CustomerViewSet(BaseAuthenticatedViewSet):
    serializer_class = CustomerSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.customers

    def get_queryset(self):
        return self.repo.customers.get_all()

class EmployeeViewSet(BaseAuthenticatedViewSet):
    serializer_class = EmployeeSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.employees

    def get_queryset(self):
        return self.repo.employees.get_all()

class SaleViewSet(BaseAuthenticatedViewSet):
    serializer_class = SaleSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.sales

    def get_queryset(self):
        return self.repo.sales.get_all()

    @action(detail=False, methods=['get'], url_path='report')
    def sales_report(self, request):
        report_data = self.repo.sales.get_sales_report()
        return Response({
            'total_records': len(report_data),
            'data': report_data
        })

class DealerProfileViewSet(BaseAuthenticatedViewSet):
    serializer_class = DealerProfileSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.dealer_profiles

    def get_queryset(self):
        return self.repo.dealer_profiles.get_all()

    @action(detail=False, methods=['get'], url_path='my-profile')
    def my_profile(self, request):
        """Get or create dealer profile for current user"""
        profile, created = self.repo.dealer_profiles.get_or_create_by_user(request.user)
        serializer = self.get_serializer(profile)
        return Response({
            'created': created,
            'profile': serializer.data
        })

    @action(detail=False, methods=['get'], url_path='high-balance')
    def high_balance(self, request):
        """Get dealers with high balance"""
        min_balance = request.query_params.get('min', 50000)
        dealers = self.repo.dealer_profiles.get_high_balance_dealers(float(min_balance))
        serializer = self.get_serializer(dealers, many=True)
        return Response(serializer.data)

class TransactionViewSet(BaseAuthenticatedViewSet):
    serializer_class = TransactionSerializer

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo_attribute = self.repo.transactions

    def get_queryset(self):
        return self.repo.transactions.get_all()

    @action(detail=False, methods=['get'], url_path='my-transactions')
    def my_transactions(self, request):
        """Get transactions for current user"""
        transactions = self.repo.transactions.get_by_dealer(request.user)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by-type')
    def by_type(self, request):
        """Get transactions filtered by type"""
        transaction_type = request.query_params.get('type', 'BUY')
        if request.user.is_authenticated:
            transactions = self.repo.transactions.get_by_dealer_and_type(
                request.user,
                transaction_type
            )
        else:
            transactions = self.repo.transactions.get_by_type(transaction_type)
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get transaction statistics for current user"""
        total_spent = self.repo.transactions.calculate_total_spent(request.user)
        total_earned = self.repo.transactions.calculate_total_earned(request.user)
        net_profit = self.repo.transactions.calculate_net_profit(request.user)

        return Response({
            'total_spent': float(total_spent),
            'total_earned': float(total_earned),
            'net_profit': float(net_profit),
            'buy_count': len(self.repo.transactions.get_buy_transactions(request.user)),
            'sell_count': len(self.repo.transactions.get_sell_transactions(request.user)),
            'modify_count': len(self.repo.transactions.get_modify_transactions(request.user)),
        })


class DealerViewSet(viewsets.ViewSet):
    """
    API для операцій дилера (buy, sell, modify, dashboard)
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='dashboard/(?P<user_id>[^/.]+)')
    def dashboard(self, request, user_id=None):
        """
        GET /api/dealer/dashboard/{user_id}/
        Отримати дані для dashboard дилера
        """
        try:
            user = User.objects.get(id=user_id)
            repo = RepositoryService()

            dealer_profile, created = repo.dealer_profiles.get_or_create_by_user(user)
            owned_cars = repo.cars.get(owner=user)
            transactions = repo.transactions.get_dealer_recent_transactions(user, limit=100)
            all_available = repo.cars.get(in_stock=True)
            # Видаляємо [:10] щоб пагінація працювала на UI рівні
            available_cars = [car for car in all_available if car.owner != user]

            return Response({
                'dealer_profile': DealerProfileSerializer(dealer_profile).data,
                'owned_cars': CarSerializer(owned_cars, many=True).data,
                'transactions': TransactionSerializer(transactions, many=True).data,
                'available_cars': CarSerializer(available_cars, many=True).data,
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], url_path='buy')
    def buy_car(self, request):
        """
        POST /api/dealer/buy/
        Body: {"user_id": 1, "car_id": 5}
        """
        user_id = request.data.get('user_id')
        car_id = request.data.get('car_id')

        if not user_id or not car_id:
            return Response({'error': 'user_id and car_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            repo = RepositoryService()
            car = repo.cars.get_by_id(car_id)

            if not car:
                return Response({'error': 'Car not found'}, status=status.HTTP_404_NOT_FOUND)

            dealer_profile, created = repo.dealer_profiles.get_or_create_by_user(user)

            # Перевірки
            if car.owner == user:
                return Response({'error': 'You already own this car!'}, status=status.HTTP_400_BAD_REQUEST)

            if dealer_profile.balance < car.price:
                return Response({
                    'error': 'Insufficient balance',
                    'required': str(car.price),
                    'balance': str(dealer_profile.balance)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Виконуємо транзакцію
            with db_transaction.atomic():
                balance_before = dealer_profile.balance

                repo.dealer_profiles.deduct_from_balance(user, car.price)
                repo.cars.update(car_id, owner=user)

                transaction_obj = repo.transactions.create(
                    dealer=user,
                    car=car,
                    transaction_type='BUY',
                    amount=-car.price,
                    description=f'Purchased {car.make} {car.model} ({car.year})',
                    balance_before=balance_before,
                    balance_after=dealer_profile.balance - car.price
                )

            return Response({
                'message': f'Successfully purchased {car.make} {car.model}',
                'transaction': TransactionSerializer(transaction_obj).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='sell')
    def sell_car(self, request):
        """
        POST /api/dealer/sell/
        Body: {"user_id": 1, "car_id": 5}
        """
        user_id = request.data.get('user_id')
        car_id = request.data.get('car_id')

        if not user_id or not car_id:
            return Response({'error': 'user_id and car_id required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            repo = RepositoryService()
            car = repo.cars.get_by_id(car_id)

            if not car or car.owner != user:
                return Response({'error': 'Car not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

            dealer_profile, created = repo.dealer_profiles.get_or_create_by_user(user)

            # Виконуємо транзакцію
            with db_transaction.atomic():
                balance_before = dealer_profile.balance

                repo.dealer_profiles.add_to_balance(user, car.price)

                transaction_obj = repo.transactions.create(
                    dealer=user,
                    car=car,
                    transaction_type='SELL',
                    amount=car.price,
                    description=f'Sold {car.make} {car.model} ({car.year})',
                    balance_before=balance_before,
                    balance_after=dealer_profile.balance + car.price
                )

                repo.cars.update(car_id, owner=None)

            return Response({
                'message': f'Successfully sold {car.make} {car.model}',
                'transaction': TransactionSerializer(transaction_obj).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], url_path='modify')
    def modify_car(self, request):
        """
        POST /api/dealer/modify/
        Body: {
            "user_id": 1,
            "car_id": 5,
            "modification_cost": 500.00,
            "price_increase": 1000.00,
            "description": "Engine upgrade"
        }
        """
        user_id = request.data.get('user_id')
        car_id = request.data.get('car_id')
        modification_cost = request.data.get('modification_cost')
        price_increase = request.data.get('price_increase')
        description = request.data.get('description', 'Car modification')

        if not all([user_id, car_id, modification_cost, price_increase]):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            modification_cost = Decimal(str(modification_cost))
            price_increase = Decimal(str(price_increase))

            if modification_cost <= 0 or price_increase <= 0:
                return Response({'error': 'Invalid amounts'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=user_id)
            repo = RepositoryService()
            car = repo.cars.get_by_id(car_id)

            if not car or car.owner != user:
                return Response({'error': 'Car not found or not owned by you'}, status=status.HTTP_404_NOT_FOUND)

            dealer_profile, created = repo.dealer_profiles.get_or_create_by_user(user)

            if dealer_profile.balance < modification_cost:
                return Response({
                    'error': 'Insufficient balance',
                    'required': str(modification_cost),
                    'balance': str(dealer_profile.balance)
                }, status=status.HTTP_400_BAD_REQUEST)

            # Виконуємо транзакцію
            with db_transaction.atomic():
                balance_before = dealer_profile.balance
                old_price = car.price
                new_price = car.price + price_increase

                repo.dealer_profiles.deduct_from_balance(user, modification_cost)
                repo.cars.update(car_id, price=new_price)

                transaction_obj = repo.transactions.create(
                    dealer=user,
                    car=car,
                    transaction_type='MODIFY',
                    amount=-modification_cost,
                    description=f'{description} - Price increased from ${old_price} to ${new_price}',
                    balance_before=balance_before,
                    balance_after=dealer_profile.balance - modification_cost
                )

            return Response({
                'message': f'Successfully modified {car.make} {car.model}',
                'new_price': str(new_price),
                'transaction': TransactionSerializer(transaction_obj).data
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='transactions/(?P<user_id>[^/.]+)')
    def transactions(self, request, user_id=None):
        """
        GET /api/dealer/transactions/{user_id}/
        Отримати всі транзакції дилера
        """
        try:
            user = User.objects.get(id=user_id)
            repo = RepositoryService()
            transactions = repo.transactions.get_by_dealer(user)

            return Response({
                'transactions': TransactionSerializer(transactions, many=True).data
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

class AnalyticsViewSet(viewsets.ViewSet):
    """
    API для аналітики з використанням pandas DataFrame
    Всі endpoint'и конвертують дані з ORM запитів у pandas для аналізу

    URI endpoints:
    - /api/analytics/sales-by-employee/
    - /api/analytics/profit-by-brand/
    - /api/analytics/transaction-dynamics/
    - /api/analytics/top-customers/
    - /api/analytics/car-price-statistics/
    - /api/analytics/dealer-balance-summary/
    """
    authentication_classes = [BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repo = RepositoryService()

    @action(detail=False, methods=['get'], url_path='sales-by-employee')
    def sales_by_employee(self, request):
        """
        GET /api/analytics/sales-by-employee/?min_sales=5

        Агрегований запит 1: Продажі по співробітниках
        Конвертує ORM QuerySet в pandas DataFrame та обчислює статистику
        """
        min_sales_count = int(request.query_params.get('min_sales', 1))

        try:
            # Отримуємо дані з ORM запиту
            data = self.repo.analytics.get_sales_by_employee(min_sales_count)

            # Конвертуємо в pandas DataFrame
            df = pd.DataFrame(data)

            if df.empty:
                return Response({
                    'message': 'No data available',
                    'orm_query_used': 'Sale.objects.select_related().values().annotate().filter().order_by()',
                    'records_count': 0
                })

            # Pandas аналіз: обчислюємо статистичні показники
            stats = {
                'mean_revenue': float(df['total_revenue'].mean()),
                'median_revenue': float(df['total_revenue'].median()),
                'min_revenue': float(df['total_revenue'].min()),
                'max_revenue': float(df['total_revenue'].max()),
                'mean_sales_count': float(df['total_sales'].mean()),
                'total_employees': len(df)
            }

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, SUM, AVG, MAX, MIN',
                    'group_by': 'employee',
                    'having_clause': f'total_sales >= {min_sales_count}',
                    'order_by': 'total_revenue DESC'
                },
                'records_count': len(df),
                'statistics': stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='profit-by-brand')
    def profit_by_brand(self, request):
        """
        GET /api/analytics/profit-by-brand/?min_cars=2

        Агрегований запит 2: Прибуток по марках автомобілів
        """
        min_cars_sold = int(request.query_params.get('min_cars', 1))

        try:
            data = self.repo.analytics.get_profit_by_car_brand(min_cars_sold)
            df = pd.DataFrame(data)

            if df.empty:
                return Response({'message': 'No data available', 'records_count': 0})

            # Pandas статистика
            stats = {
                'mean_revenue_per_brand': float(df['total_revenue'].mean()),
                'median_revenue_per_brand': float(df['total_revenue'].median()),
                'highest_revenue_brand': df.loc[df['total_revenue'].idxmax()]['car__make'],
                'lowest_revenue_brand': df.loc[df['total_revenue'].idxmin()]['car__make'],
                'total_brands': len(df),
                'total_revenue_all_brands': float(df['total_revenue'].sum())
            }

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, SUM, AVG, MAX',
                    'group_by': 'car__make',
                    'having_clause': f'cars_sold >= {min_cars_sold}',
                    'order_by': 'total_revenue DESC'
                },
                'records_count': len(df),
                'statistics': stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='transaction-dynamics')
    def transaction_dynamics(self, request):
        """
        GET /api/analytics/transaction-dynamics/?min_amount=1000

        Агрегований запит 3: Динаміка транзакцій дилерів по типах
        """
        min_amount = float(request.query_params.get('min_amount', 0))

        try:
            data = self.repo.analytics.get_transaction_dynamics_by_dealer(min_amount)
            df = pd.DataFrame(data)

            if df.empty:
                return Response({'message': 'No data available', 'records_count': 0})

            # Pandas групування та аналіз
            stats = {
                'mean_transaction_count': float(df['transaction_count'].mean()),
                'median_transaction_count': float(df['transaction_count'].median()),
                'total_amount_all_dealers': float(df['total_amount'].sum()),
                'mean_amount_per_dealer': float(df['total_amount'].mean()),
                'unique_dealers': df['dealer__username'].nunique(),
                'transaction_types': df['transaction_type'].unique().tolist()
            }

            # Групуємо по типу транзакції для додаткової статистики
            type_stats = df.groupby('transaction_type').agg({
                'total_amount': 'sum',
                'transaction_count': 'sum'
            }).to_dict(orient='index')

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, SUM, AVG, MAX',
                    'group_by': 'dealer, transaction_type',
                    'having_clause': f'total_amount >= {min_amount}',
                    'order_by': 'dealer__username, total_amount DESC'
                },
                'records_count': len(df),
                'statistics': stats,
                'by_transaction_type': type_stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='top-customers')
    def top_customers(self, request):
        """
        GET /api/analytics/top-customers/?limit=10

        Агрегований запит 4: Топ клієнтів по витратам
        """
        limit = int(request.query_params.get('limit', 10))

        try:
            data = self.repo.analytics.get_top_customers_by_spending(limit)
            df = pd.DataFrame(data)

            if df.empty:
                return Response({'message': 'No data available', 'records_count': 0})

            # Pandas статистика
            stats = {
                'mean_spending': float(df['total_spent'].mean()),
                'median_spending': float(df['total_spent'].median()),
                'min_spending': float(df['total_spent'].min()),
                'max_spending': float(df['total_spent'].max()),
                'total_revenue': float(df['total_spent'].sum()),
                'mean_cars_per_customer': float(df['cars_purchased'].mean())
            }

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, SUM, AVG, MAX',
                    'group_by': 'customer',
                    'order_by': 'total_spent DESC',
                    'limit': limit
                },
                'records_count': len(df),
                'statistics': stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='car-price-statistics')
    def car_price_statistics(self, request):
        """
        GET /api/analytics/car-price-statistics/?min_cars=3

        Агрегований запит 5: Статистика цін автомобілів по рокам виробництва
        """
        min_cars_count = int(request.query_params.get('min_cars', 1))

        try:
            data = self.repo.analytics.get_car_price_statistics_by_year(min_cars_count)
            df = pd.DataFrame(data)

            if df.empty:
                return Response({'message': 'No data available', 'records_count': 0})

            # Конвертуємо Decimal в float для pandas
            for col in ['average_price', 'max_price', 'min_price']:
                if col in df.columns:
                    df[col] = df[col].astype(float)

            # Pandas статистика
            stats = {
                'overall_mean_price': float(df['average_price'].mean()),
                'overall_median_price': float(df['average_price'].median()),
                'year_range': {
                    'oldest': int(df['year'].min()),
                    'newest': int(df['year'].max())
                },
                'total_cars': int(df['cars_count'].sum()),
                'total_in_stock': int(df['in_stock_count'].sum()),
                'most_expensive_year': int(df.loc[df['average_price'].idxmax()]['year']),
                'cheapest_year': int(df.loc[df['average_price'].idxmin()]['year'])
            }

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, AVG, MAX, MIN, COUNT with Q filter',
                    'group_by': 'year',
                    'having_clause': f'cars_count >= {min_cars_count}',
                    'order_by': 'year DESC'
                },
                'records_count': len(df),
                'statistics': stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='dealer-balance-summary')
    def dealer_balance_summary(self, request):
        """
        GET /api/analytics/dealer-balance-summary/?min_transactions=5

        Агрегований запит 6: Сумарна інформація про баланси дилерів
        """
        min_transactions = int(request.query_params.get('min_transactions', 1))

        try:
            data = self.repo.analytics.get_dealer_balance_summary(min_transactions)
            df = pd.DataFrame(data)

            if df.empty:
                return Response({'message': 'No data available', 'records_count': 0})

            # Конвертуємо Decimal в float
            for col in ['current_balance', 'total_buy_amount', 'total_sell_amount', 'average_transaction']:
                if col in df.columns:
                    df[col] = df[col].fillna(0).astype(float)

            # Pandas статистика
            stats = {
                'mean_balance': float(df['current_balance'].mean()),
                'median_balance': float(df['current_balance'].median()),
                'min_balance': float(df['current_balance'].min()),
                'max_balance': float(df['current_balance'].max()),
                'total_dealers': len(df),
                'total_transactions': int(df['total_transactions'].sum()),
                'total_buy_operations': int(df['buy_transactions'].sum()),
                'total_sell_operations': int(df['sell_transactions'].sum()),
                'total_modify_operations': int(df['modify_transactions'].sum())
            }

            return Response({
                'query_info': {
                    'orm_aggregations': 'COUNT, MAX, SUM with Q filters, AVG',
                    'group_by': 'dealer',
                    'having_clause': f'total_transactions >= {min_transactions}',
                    'order_by': 'current_balance DESC'
                },
                'records_count': len(df),
                'statistics': stats,
                'data': df.to_dict(orient='records')
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import BenchmarkResult
import json


def benchmark_dashboard(request):
    return render(request, 'repo_practice/benchmark_dashboard.html')


@require_http_methods(["POST"])
def run_benchmark(request):
    try:
        data = json.loads(request.body)
        execution_type = data.get('execution_type', 'threading')
        num_workers = int(data.get('num_workers', 4))
        num_queries = int(data.get('num_queries', 100))
        batch_size = int(data.get('batch_size', 10))

        from repo_practice.benchmarks.run_benchmarks import run_experiment

        benchmark = run_experiment(
            execution_type=execution_type,
            num_workers=num_workers,
            num_queries=num_queries,
            batch_size=batch_size
        )

        return JsonResponse({
            'success': True,
            'benchmark_id': benchmark.id,
            'execution_time': benchmark.execution_time,
            'cpu_usage': benchmark.cpu_usage,
            'memory_usage': benchmark.memory_usage
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_benchmark_results(request):
    execution_type = request.GET.get('execution_type', None)

    queryset = BenchmarkResult.objects.all()
    if execution_type:
        queryset = queryset.filter(execution_type=execution_type)

    results = list(queryset.values(
        'id', 'execution_type', 'num_workers', 'batch_size',
        'num_queries', 'execution_time', 'cpu_usage', 'memory_usage', 'timestamp'
    ))

    return JsonResponse({'results': results})


@require_http_methods(["DELETE"])
def clear_benchmark_results(request):
    count = BenchmarkResult.objects.all().delete()[0]
    return JsonResponse({'success': True, 'deleted_count': count})


@require_http_methods(["POST"])
def create_demo_data(request):
    try:
        from repo_practice.benchmarks.run_benchmarks import run_experiment

        created = 0
        for workers in [2, 4, 8]:
            for exec_type in ['threading']:
                if BenchmarkResult.objects.filter(
                    execution_type=exec_type,
                    num_workers=workers
                ).count() == 0:
                    run_experiment(
                        execution_type=exec_type,
                        num_workers=workers,
                        num_queries=30,
                        batch_size=10
                    )
                    created += 1

        return JsonResponse({'success': True, 'created_count': created})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


