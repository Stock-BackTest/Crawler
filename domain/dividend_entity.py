from dataclasses import dataclass
from datetime import date


@dataclass
class DividendEntity:
  isin: str                 # 식별번호
  pay_base_date: date       # 지급기준일
  actual_pay_date: date     # 실지급일
  div_type: str             # 배당구분
  dist_per_share: float     # 시가대비분배율 (BUNBE)
  tax_std: float            # 결산과표기준
  estm_stdprc: float        # 주당분배금