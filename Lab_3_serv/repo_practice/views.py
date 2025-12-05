from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomerSerializer, EmployeeSerializer, SaleSerializer, DealerProfileSerializer, TransactionSerializer

from .serializers import CarSerializer
from .services.repo_service import RepositoryService

from rest_framework.decorators import action
from rest_framework.response import Response


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
