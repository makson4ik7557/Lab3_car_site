from typing import List, Optional
from decimal import Decimal
from django.contrib.auth.models import User
from ..models import Transaction, Car
from .base_repo import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):
    def get_all(self) -> List[Transaction]:
        return list(Transaction.objects.all())

    def get_by_id(self, id: int) -> Optional[Transaction]:
        try:
            return Transaction.objects.get(id=id)
        except Transaction.DoesNotExist:
            return None

    def create(self, **kwargs) -> Transaction:
        return Transaction.objects.create(**kwargs)

    def update(self, id: int, **kwargs) -> Optional[Transaction]:
        try:
            transaction = Transaction.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(transaction, key, value)
            transaction.save()
            return transaction
        except Transaction.DoesNotExist:
            return None

    def delete(self, id: int) -> bool:
        try:
            transaction = Transaction.objects.get(id=id)
            transaction.delete()
            return True
        except Transaction.DoesNotExist:
            return False

    def get_by_dealer(self, dealer: User, limit: int = None) -> List[Transaction]:
        """Get all transactions for a specific dealer"""
        queryset = Transaction.objects.filter(dealer=dealer)
        if limit:
            queryset = queryset[:limit]
        return list(queryset)

    def get_by_type(self, transaction_type: str) -> List[Transaction]:
        """Get transactions by type (BUY, SELL, MODIFY)"""
        return list(Transaction.objects.filter(transaction_type=transaction_type))

    def get_by_dealer_and_type(self, dealer: User, transaction_type: str) -> List[Transaction]:
        """Get transactions for a dealer filtered by type"""
        return list(Transaction.objects.filter(dealer=dealer, transaction_type=transaction_type))

    def get_by_car(self, car: Car) -> List[Transaction]:
        """Get all transactions related to a specific car"""
        return list(Transaction.objects.filter(car=car))

    def get_recent_transactions(self, limit: int = 20) -> List[Transaction]:
        """Get most recent transactions"""
        return list(Transaction.objects.all()[:limit])

    def get_dealer_recent_transactions(self, dealer: User, limit: int = 20) -> List[Transaction]:
        """Get most recent transactions for a specific dealer"""
        return list(Transaction.objects.filter(dealer=dealer)[:limit])

    def get_buy_transactions(self, dealer: User = None) -> List[Transaction]:
        """Get all BUY transactions, optionally filtered by dealer"""
        queryset = Transaction.objects.filter(transaction_type='BUY')
        if dealer:
            queryset = queryset.filter(dealer=dealer)
        return list(queryset)

    def get_sell_transactions(self, dealer: User = None) -> List[Transaction]:
        """Get all SELL transactions, optionally filtered by dealer"""
        queryset = Transaction.objects.filter(transaction_type='SELL')
        if dealer:
            queryset = queryset.filter(dealer=dealer)
        return list(queryset)

    def get_modify_transactions(self, dealer: User = None) -> List[Transaction]:
        """Get all MODIFY transactions, optionally filtered by dealer"""
        queryset = Transaction.objects.filter(transaction_type='MODIFY')
        if dealer:
            queryset = queryset.filter(dealer=dealer)
        return list(queryset)

    def calculate_total_spent(self, dealer: User) -> Decimal:
        """Calculate total money spent by dealer (negative amounts)"""
        transactions = Transaction.objects.filter(dealer=dealer, amount__lt=0)
        return sum(t.amount for t in transactions) if transactions else Decimal('0.00')

    def calculate_total_earned(self, dealer: User) -> Decimal:
        """Calculate total money earned by dealer (positive amounts)"""
        transactions = Transaction.objects.filter(dealer=dealer, amount__gt=0)
        return sum(t.amount for t in transactions) if transactions else Decimal('0.00')

    def calculate_net_profit(self, dealer: User) -> Decimal:
        """Calculate net profit/loss for dealer"""
        spent = self.calculate_total_spent(dealer)
        earned = self.calculate_total_earned(dealer)
        return earned + spent  # spent is negative, so we add

    def get_transactions_by_date_range(self, dealer: User, start_date, end_date) -> List[Transaction]:
        """Get transactions within a date range"""
        return list(Transaction.objects.filter(
            dealer=dealer,
            created_at__gte=start_date,
            created_at__lte=end_date
        ))

