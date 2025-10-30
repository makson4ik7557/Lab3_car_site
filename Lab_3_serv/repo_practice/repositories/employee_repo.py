from typing import List, Optional
from ..models import Employee
from .base_repo import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    def get_all(self) -> List[Employee]:
        return list(Employee.objects.all())

    def get_by_id(self, id: int) -> Optional[Employee]:
        try:
            return Employee.objects.get(id=id)
        except Employee.DoesNotExist:
            return None

    def create(self, **kwargs) -> Employee:
        return Employee.objects.create(**kwargs)

    def get_by_position(self, position: str) -> List[Employee]:
        return list(Employee.objects.filter(position__iexact=position))