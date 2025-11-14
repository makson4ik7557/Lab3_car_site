from typing import List, Optional
from ..models import Customer
from .base_repo import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def get(self, id: Optional[int] = None, **filters) -> Optional[Customer] | List[Customer]:
        if id is not None:
            try:
                return Customer.objects.get(id=id)
            except Customer.DoesNotExist:
                return None
        if filters:
            return list(Customer.objects.filter(**filters))
        return list(Customer.objects.all())

    def get_all(self) -> List[Customer]:
        return list(Customer.objects.all())

    def get_by_id(self, id: int) -> Optional[Customer]:
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None

    def create(self, **kwargs) -> Customer:
        return Customer.objects.create(**kwargs)

    def add(self, **kwargs) -> Customer:
        return self.create(**kwargs)

    def update(self, id: int, **kwargs) -> Optional[Customer]:
        try:
            customer = Customer.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(customer, key, value)
            customer.save()
            return customer
        except Customer.DoesNotExist:
            return None

    def delete(self, id: int) -> bool:
        try:
            customer = Customer.objects.get(id=id)
            customer.delete()
            return True
        except Customer.DoesNotExist:
            return False

    def get_by_email(self, email: str) -> Optional[Customer]:
        try:
            return Customer.objects.get(email=email)
        except Customer.DoesNotExist:
            return None