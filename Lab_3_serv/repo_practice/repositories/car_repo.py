from typing import List, Optional
from ..models import Car
from .base_repo import BaseRepository


class CarRepository(BaseRepository[Car]):
    def get_all(self) -> List[Car]:
        return list(Car.objects.all())

    def get_by_id(self, id: int) -> Optional[Car]:
        try:
            return Car.objects.get(id=id)
        except Car.DoesNotExist:
            return None

    def create(self, **kwargs) -> Car:
        return Car.objects.create(**kwargs)

    def get_available_cars(self) -> List[Car]:
        return list(Car.objects.filter(in_stock=True))

    def get_cars_by_make(self, make: str) -> List[Car]:
        return list(Car.objects.filter(make__iexact=make))

    def get_premium_cars(self, min_price: int = 80000) -> List[Car]:
        return list(Car.objects.filter(price__gte=min_price))

    def get_cars_by_year_range(self, start_year: int, end_year: int) -> List[Car]:
        return list(Car.objects.filter(year__gte=start_year, year__lte=end_year))

    def get_most_expensive(self) -> Optional[Car]:
        return Car.objects.order_by('-price').first()

    def get_cheapest(self) -> Optional[Car]:
        return Car.objects.order_by('price').first()
