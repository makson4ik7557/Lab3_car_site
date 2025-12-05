from rest_framework import serializers
from .models import Car, Customer, Employee, Sale, DealerProfile, Transaction

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = '__all__'

class DealerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DealerProfile
        fields = ['id', 'user', 'username', 'balance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class TransactionSerializer(serializers.ModelSerializer):
    dealer_username = serializers.CharField(source='dealer.username', read_only=True)
    car_info = serializers.SerializerMethodField()

    class Meta:
        model = Transaction
        fields = ['id', 'dealer', 'dealer_username', 'car', 'car_info',
                  'transaction_type', 'amount', 'description',
                  'balance_before', 'balance_after', 'created_at']
        read_only_fields = ['created_at']

    def get_car_info(self, obj):
        if obj.car:
            return f"{obj.car.make} {obj.car.model} ({obj.car.year})"
        return None

