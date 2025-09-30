from __future__ import annotations
from typing import Iterable, Dict, List, Optional, Sequence
from datetime import datetime
import logging

from domain.normalizer_interface import Normalizer


def _norm_date(s: Optional[str]) -> Optional[str]:
    if not s: return None
    s = s.strip()
    if len(s) == 8 and s.isdigit():  # YYYYMMDD -> YYYY-MM-DD
        return f"{s[:4]}-{s[4:6]}-{s[6:]}"
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return s

def _norm_number(s: Optional[str]) -> str:
    if s is None: return ""
    s = s.strip()
    if not s: return ""
    return s.replace(",", "")

def _pick(d: dict, candidates: List[str]) -> Optional[str]:
    for k in candidates:
        v = d.get(k)
        if v is not None and str(v).strip() != "":
            return str(v)
    return None

class DefaultNormalizer(Normalizer):
    def __init__(
        self,
        date_keys: Sequence[str] = ("pay_base_date", "actual_pay_date"),
        number_keys: Sequence[str] = ("dist_per_share", "estm_stdprc"),
        required_fields: Sequence[str] = (
            "isin",
            "pay_base_date",      # 지급 기준일
            "actual_pay_date",    # 실 지급일
            "div_type",           # 배당 구분
            "dist_per_share",     # 분배금
            "estm_stdprc",        # 기준가
        ),
        strict: bool = True,
    ):
        self.DATE_KEYS = set(date_keys)
        self.NUMBER_KEYS = set(number_keys)
        self.REQUIRED_FIELDS = list(required_fields)
        self.strict = strict

    def normalize(
        self,
        records: Iterable[dict],
        mapping: Dict[str, List[str]],
        context: Optional[Dict[str, str]] = None,
    ) -> List[dict]:
        ctx = context or {}
        out: List[dict] = []

        for r in records:
            std: Dict[str, Optional[str]] = {}

            for target, candidates in mapping.items():
                val = _pick(r, candidates)
                if val is None:
                    val = ctx.get(target)

                if target in self.DATE_KEYS:
                    std[target] = _norm_date(val) if val else None
                elif target in self.NUMBER_KEYS:
                    std[target] = _norm_number(val)
                else:
                    std[target] = (val or "").strip()

            missing: List[str] = []
            for f in self.REQUIRED_FIELDS:
                v = std.get(f, None)
                if self.strict:
                    if v is None or (isinstance(v, str) and v.strip() == ""):
                        missing.append(f)
                else:
                    if f not in std:
                        missing.append(f)

            if missing:
                logging.warning(f'{r} is missing field: {missing}')
                continue

            out.append(std)

        return out
