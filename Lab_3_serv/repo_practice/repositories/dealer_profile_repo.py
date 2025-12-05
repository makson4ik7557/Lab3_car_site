from typing import List, Optional
from django.contrib.auth.models import User
from ..models import DealerProfile
from .base_repo import BaseRepository


class DealerProfileRepository(BaseRepository[DealerProfile]):
    def get_all(self) -> List[DealerProfile]:
        return list(DealerProfile.objects.all())

    def get_by_id(self, id: int) -> Optional[DealerProfile]:
        try:
            return DealerProfile.objects.get(id=id)
        except DealerProfile.DoesNotExist:
            return None

    def create(self, **kwargs) -> DealerProfile:
        return DealerProfile.objects.create(**kwargs)

    def update(self, id: int, **kwargs) -> Optional[DealerProfile]:
        try:
            profile = DealerProfile.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(profile, key, value)
            profile.save()
            return profile
        except DealerProfile.DoesNotExist:
            return None

    def delete(self, id: int) -> bool:
        try:
            profile = DealerProfile.objects.get(id=id)
            profile.delete()
            return True
        except DealerProfile.DoesNotExist:
            return False

    def get_by_user(self, user: User) -> Optional[DealerProfile]:
        """Get dealer profile by user"""
        try:
            return DealerProfile.objects.get(user=user)
        except DealerProfile.DoesNotExist:
            return None

    def get_or_create_by_user(self, user: User, defaults: dict = None) -> tuple[DealerProfile, bool]:
        """Get or create dealer profile for a user"""
        if defaults is None:
            defaults = {'balance': 10000.00}
        return DealerProfile.objects.get_or_create(user=user, defaults=defaults)

    def update_balance(self, user: User, new_balance: float) -> Optional[DealerProfile]:
        """Update dealer's balance"""
        try:
            profile = DealerProfile.objects.get(user=user)
            profile.balance = new_balance
            profile.save()
            return profile
        except DealerProfile.DoesNotExist:
            return None

    def add_to_balance(self, user: User, amount: float) -> Optional[DealerProfile]:
        """Add amount to dealer's balance"""
        try:
            profile = DealerProfile.objects.get(user=user)
            profile.balance += amount
            profile.save()
            return profile
        except DealerProfile.DoesNotExist:
            return None

    def deduct_from_balance(self, user: User, amount: float) -> Optional[DealerProfile]:
        """Deduct amount from dealer's balance"""
        try:
            profile = DealerProfile.objects.get(user=user)
            profile.balance -= amount
            profile.save()
            return profile
        except DealerProfile.DoesNotExist:
            return None

    def get_high_balance_dealers(self, min_balance: float = 50000.00) -> List[DealerProfile]:
        """Get dealers with balance above threshold"""
        return list(DealerProfile.objects.filter(balance__gte=min_balance))

    def get_low_balance_dealers(self, max_balance: float = 1000.00) -> List[DealerProfile]:
        """Get dealers with balance below threshold"""
        return list(DealerProfile.objects.filter(balance__lte=max_balance))

