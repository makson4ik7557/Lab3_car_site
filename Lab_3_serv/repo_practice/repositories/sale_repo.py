from typing import List, Optional
from django.db.models import Count, Sum, Avg, Max, Min
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

    def update(self, id: int, **kwargs) -> Optional[Sale]:
        try:
            sale = Sale.objects.get(id=id)
            for key, value in kwargs.items():
                setattr(sale, key, value)
            sale.save()
            return sale
        except Sale.DoesNotExist:
            return None

    def delete(self, id: int) -> bool:
        try:
            sale = Sale.objects.get(id=id)
            sale.delete()
            return True
        except Sale.DoesNotExist:
            return False

    def get_sales_by_customer(self, customer_id: int) -> List[Sale]:
        return list(Sale.objects.filter(customer_id=customer_id).select_related('car', 'employee'))

    def get_sales_report(self) -> List[dict]:
        """Звіт: статистика продажів за марками та моделями машин"""
        return list(
            Sale.objects
            .values('car__make', 'car__model')
            .annotate(
                total_sales=Count('id'),
                total_revenue=Sum('sale_price'),
                average_price=Avg('sale_price'),
                max_price=Max('sale_price'),
                min_price=Min('sale_price')
            )
            .order_by('-total_sales')
        )