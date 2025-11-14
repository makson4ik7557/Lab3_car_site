from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic
from django.db import models

T = TypeVar('T', bound=models.Model)


class BaseRepository(Generic[T], ABC):
    @abstractmethod
    def get_all(self) -> List[T]:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[T]:
        pass

    @abstractmethod
    def create(self, **kwargs) -> T:
        pass

    @abstractmethod
    def update(self, id: int, **kwargs) -> Optional[T]:
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass
