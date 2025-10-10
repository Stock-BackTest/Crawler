from __future__ import annotations

from datetime import date
from typing import List

from domain.dividend_entity import DividendEntity

DIV_TYPE_MAX_LEN = 50

def make_dividend(
    *,
    isin: str = "KR7276970001",
    pay_base_date: date = date(2025, 9, 24),
    actual_pay_date: date | None = date(2025, 9, 26),
    div_type: str = "이익분배",
    dist_per_share: float = 1.52833,
    tax_std: float = 1111.11,
    estm_stdprc: float = 116.0,
) -> DividendEntity:
    return DividendEntity(
        isin=isin,
        pay_base_date=pay_base_date,
        actual_pay_date=actual_pay_date,
        div_type=div_type,
        dist_per_share=dist_per_share,
        tax_std=tax_std,
        estm_stdprc=estm_stdprc,
    )

def sample_pair() -> List[DividendEntity]:
    return [
        make_dividend(
            isin="KR7276970001",
            pay_base_date=date(2025, 9, 24),
            actual_pay_date=date(2025, 9, 26),
            div_type="이익분배",
            dist_per_share=1.52833,
            tax_std=1111.11,
            estm_stdprc=116.0,
        ),
        make_dividend(
            isin="KR7407170000",
            pay_base_date=date(2025, 9, 21),
            actual_pay_date=date(2025, 9, 22),
            div_type="청산분배",
            dist_per_share=0.0,
            tax_std=10000.00,
            estm_stdprc=9944.968864,
        ),
    ]

def updated_for_upsert() -> DividendEntity:
    return make_dividend(
        isin="KR7276970001",
        pay_base_date=date(2025, 9, 24),
        actual_pay_date=date(2025, 9, 27),
        div_type="이익분배",
        dist_per_share=1.6,
        tax_std=2222.22,
        estm_stdprc=120.0,
    )

def div_type_exact_len() -> str:
    return "X" * DIV_TYPE_MAX_LEN

def div_type_too_long() -> str:
    return "Y" * (DIV_TYPE_MAX_LEN + 1)
