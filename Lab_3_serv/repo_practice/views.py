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
            transactions = repo.transactions.get_dealer_recent_transactions(user, limit=20)
            all_available = repo.cars.get(in_stock=True)
            available_cars = [car for car in all_available if car.owner != user][:10]

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
