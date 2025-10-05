from datetime import datetime, date
from typing import Iterable, Dict, List, Optional

from domain.dividend_entity import DividendEntity
from domain.normalizer_interface import Normalizer


def _parse_date(s: Optional[str]) -> Optional[date]:
  if not s:
    return None
  s = s.strip()
  if len(s) == 8 and s.isdigit():  # YYYYMMDD
    return datetime.strptime(s, "%Y%m%d").date()
  for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
    try:
      return datetime.strptime(s, fmt).date()
    except ValueError:
      pass
  return None


def _parse_float(s: Optional[str]) -> float:
  if not s:
    return 0.0
  s2 = s.strip().replace(",", "")
  if s2 == "":
    return 0.0
  try:
    return float(s2)
  except ValueError:
    return 0.0


def _pick(d: dict, candidates: List[str]) -> Optional[str]:
  for k in candidates:
    v = d.get(k)
    if v is not None and str(v).strip() != "":
      return str(v)
  return None


class DefaultNormalizer(Normalizer):
  def __init__(self):
    pass

  def normalize(
      self,
      records: Iterable[dict],
      mapping: Dict[str, List[str]],
  ) -> List[DividendEntity]:
    out: List[DividendEntity] = []

    for r in records:
      isin = _pick(r, mapping.get("isin", [])) or ""
      pay_base_date = _parse_date(_pick(r, mapping.get("pay_base_date", [])))
      actual_pay_date = _parse_date(
        _pick(r, mapping.get("actual_pay_date", [])))
      div_type = _pick(r, mapping.get("div_type", [])) or ""
      dist_per_share = _parse_float(_pick(r, mapping.get("dist_per_share", [])))
      estm_stdprc = _parse_float(_pick(r, mapping.get("estm_stdprc", [])))

      ev = DividendEntity(
          isin=isin,
          pay_base_date=pay_base_date,
          actual_pay_date=actual_pay_date,
          div_type=div_type,
          dist_per_share=dist_per_share,
          estm_stdprc=estm_stdprc,
      )
      out.append(ev)

    return out
