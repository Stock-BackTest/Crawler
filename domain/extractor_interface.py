from typing import Protocol, Any, Iterable, Optional, Mapping

class RawResponse:
    def __init__(self, text: str, mime: Optional[str] = None, meta: Optional[Mapping[str, Any]] = None):
        self.text = text
        self.mime = mime
        self.meta = meta or {}

class Extractor(Protocol):
    def can_handle(self, raw: RawResponse) -> bool: ...
    def parse(self, raw: RawResponse) -> Iterable[dict]: ...
