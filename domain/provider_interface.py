from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class BaseProviderRequest(ABC):
  params: Mapping[str, str] = field(default_factory=dict)


class ProviderInterface(ABC):
TReq = TypeVar("TReq", bound=BaseProviderRequest)
class DividendProvider(ABC, Generic[TReq]):
  @abstractmethod
  def fetch(self, req: BaseProviderRequest) -> str:
    raise NotImplemented
