from typing import List, Optional
from ..models import Sale
from .base_repo import BaseRepository


class SaleRepository(BaseRepository[Sale]):
    def get(self, id: Optional[int] = None, **filters) -> Optional[Sale] | List[Sale]:
        if id is not None:
            try:
                return Sale.objects.select_related('car', 'customer', 'employee').get(id=id)
            except Sale.DoesNotExist:
                return None
        if filters:
            return list(Sale.objects.select_related('car', 'customer', 'employee').filter(**filters))
        return list(Sale.objects.select_related('car', 'customer', 'employee').all())

    def get_all(self) -> List[Sale]:
        return list(Sale.objects.select_related('car', 'customer', 'employee').all())

    def get_by_id(self, id: int) -> Optional[Sale]:
        try:
            return Sale.objects.select_related('car', 'customer', 'employee').get(id=id)
        except Sale.DoesNotExist:
            return None

    def create(self, **kwargs) -> Sale:
        return Sale.objects.create(**kwargs)

    def add(self, **kwargs) -> Sale:
        return self.create(**kwargs)

    def get_sales_by_customer(self, customer_id: int) -> List[Sale]:
        return list(Sale.objects.filter(customer_id=customer_id).select_related('car', 'employee'))