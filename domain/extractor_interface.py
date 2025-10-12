from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Mapping

import requests


class RawResponse:
    def __init__(self, text: str, mime: Optional[str] = None, meta: Optional[Mapping[str, Any]] = None):
        self.text = text
        self.mime = mime
        self.meta = meta or {}

class Extractor(Protocol):
    def can_handle(self, raw: RawResponse) -> bool: ...
    def parse(self, raw: RawResponse) -> Iterable[dict]: ...

class DividendExtractor(ABC):
  @abstractmethod
  def can_handle(self, raw: RawResponse) -> bool: ...

  @abstractmethod
  def parse(self, raw: RawResponse) -> Iterable[dict]: ...
