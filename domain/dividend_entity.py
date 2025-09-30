from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class DividendEntity:
  isin: str
  pay_base_date: date
  actual_pay_date: date
  div_type: str
  dist_per_share: float
  estm_stdprc: float