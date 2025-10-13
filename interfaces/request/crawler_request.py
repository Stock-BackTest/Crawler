from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional, Mapping, Any


def _parse_date(s: str | None) -> Optional[date]:
  if not s:
    return None
  s = s.strip()
  if len(s) == 8 and s.isdigit():
    return date(int(s[0:4]), int(s[4:6]), int(s[6:8]))
  if len(s) == 10 and s[4] == '-' and s[7] == '-':
    return date.fromisoformat(s)
  raise ValueError(f"Invalid date format: {s}")


@dataclass(frozen=True)
class CrawlerRequest:
  provider: str
  from_dt: Optional[date] = None
  to_dt: Optional[date] = None
  max_page: int = 1
  size: int = 30
  extra: Mapping[str, Any] = None

  @classmethod
  def from_cli(cls, ns) -> "CrawlerRequest":
    from_dt = _parse_date(getattr(ns, "from_dt", None))
    to_dt = _parse_date(getattr(ns, "to_dt", None))
    max_page = getattr(ns, "max_page", None) or 1
    size = getattr(ns, "size", None) or 30

    if max_page is not None and max_page <= 0:
      raise ValueError("--max-page must be positive")
    if size is not None and size <= 0:
      raise ValueError("--size must be positive")

    return cls(
        provider=ns.provider,
        from_dt=from_dt,
        to_dt=to_dt,
        max_page=max_page,
        size=size,
        extra={},
    )

  def to_provider_kwargs(self) -> dict[str, Any]:
    return {
      "from_date": self.from_dt,
      "to_date": self.to_dt,
      "max_page": self.max_page,
      "size": self.size,
      **(self.extra or {}),
    }
