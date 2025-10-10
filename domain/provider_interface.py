from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class BaseProviderRequest(ABC):
  params: Mapping[str, str] = field(default_factory=dict)


class ProviderInterface(ABC):
  @abstractmethod
  def fetch(self, req: BaseProviderRequest) -> str:
    raise NotImplemented
