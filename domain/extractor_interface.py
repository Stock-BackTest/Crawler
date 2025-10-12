from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Mapping

import requests


class RawResponse:
  def __init__(self, text: str, mime: Optional[str] = None,
      meta: Optional[Mapping[str, Any]] = None):
    self.text = text
    self.mime = mime
    self.meta = meta or {}

  @staticmethod
  def convert(resp: requests.Response) -> "RawResponse":
    content_type = resp.headers.get("Content-Type", "").split(";")[
                     0].strip() or None

    return RawResponse(
        text=resp.text,
        mime=content_type,
        meta={
          "status_code": resp.status_code,
          "url": resp.url,
          "headers": dict(resp.headers),
        },
    )


class DividendExtractor(ABC):
  @abstractmethod
  def can_handle(self, raw: RawResponse) -> bool: ...

  @abstractmethod
  def parse(self, raw: RawResponse) -> Iterable[dict]: ...
