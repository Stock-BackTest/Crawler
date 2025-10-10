from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from domain.dividend_entity import DividendEntity

class DividendRepository(ABC):

    @abstractmethod
    def save(self, records: List[DividendEntity]) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, query: Optional[Dict] = None) -> List[DividendEntity]:
        raise NotImplementedError
