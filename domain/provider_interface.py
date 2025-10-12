from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Mapping, TypeVar, Generic

import requests


@dataclass
class BaseProviderRequest(ABC):
  params: Mapping[str, str] = field(default_factory=dict)


TReq = TypeVar("TReq", bound=BaseProviderRequest)


class DividendProvider(ABC, Generic[TReq]):
  @abstractmethod
  def fetch(self, req: BaseProviderRequest) -> str:
  def fetch(self, req: BaseProviderRequest) -> requests.Response:
    raise NotImplemented

    raise NotImplemented
