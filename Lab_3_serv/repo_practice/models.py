from django.db import models
from django.contrib.auth.models import User

class Car(models.Model):
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    in_stock = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_cars')

    class Meta:
        db_table = 'cars'
        managed = True

    def __str__(self):
        return f"{self.make} {self.model}"

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'customers'
        managed = True

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    position = models.CharField(max_length=50)
    hire_date = models.DateField()

    class Meta:
        db_table = 'employees'
        managed = True

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Sale(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    sale_price = models.DecimalField(max_digits=12, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sales'
        managed = True

    def __str__(self):
        return f"Sale #{self.id}"

class DealerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dealer_profile')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=10000.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'dealer_profiles'
        managed = True

    def __str__(self):
        return f"{self.user.username} - Balance: ${self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('BUY', 'Buy Car'),
        ('SELL', 'Sell Car'),
        ('MODIFY', 'Modify Car'),
    ]

    dealer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    car = models.ForeignKey(Car, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        managed = True
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.dealer.username} - {self.transaction_type} - ${self.amount}"
