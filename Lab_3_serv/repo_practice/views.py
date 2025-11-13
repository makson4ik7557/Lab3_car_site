from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import CustomerSerializer, EmployeeSerializer, SaleSerializer

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
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.delete()

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
