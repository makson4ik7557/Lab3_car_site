from django.contrib import admin
from .models import Car, Customer, Employee, Sale, DealerProfile, Transaction

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('make', 'model', 'year', 'price', 'in_stock', 'owner', 'created_at')
    list_filter = ('in_stock', 'year')
    search_fields = ('make', 'model')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'position', 'hire_date')
    search_fields = ('first_name', 'last_name', 'position')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'car', 'customer', 'employee', 'sale_price', 'sale_date')
    list_filter = ('sale_date',)

@admin.register(DealerProfile)
class DealerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('dealer', 'transaction_type', 'car', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('dealer__username', 'description')
    readonly_fields = ('created_at',)
