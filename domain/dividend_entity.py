from dataclasses import dataclass
from datetime import date

from sqlalchemy import String, Date, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
  pass


@dataclass
class DividendEntity(Base):
  __tablename__ = "dividends"

  # 식별번호
  isin: Mapped[str] = mapped_column(String(20), primary_key=True)

  # 지급기준일
  pay_base_date: Mapped[date] = mapped_column(Date, primary_key=True)

  # 실지급일
  actual_pay_date: Mapped[date | None] = mapped_column(Date, nullable=True)

  # 배당구분
  div_type: Mapped[str] = mapped_column(String(50), nullable=False, default="")

  # 시가대비분배율 (BUNBE)
  dist_per_share: Mapped[float] = mapped_column(Float, nullable=False,
                                                default=0.0)

  # 결산과표기준
  tax_std: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

  # 주당분배금
  estm_stdprc: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

  def __init__(
      self,
      isin: str,
      pay_base_date: date,
      actual_pay_date: date | None,
      div_type: str,
      dist_per_share: float,
      tax_std: float,
      estm_stdprc: float,
  ):
    self.isin = isin
    self.pay_base_date = pay_base_date
    self.actual_pay_date = actual_pay_date
    self.div_type = div_type
    self.dist_per_share = dist_per_share
    self.tax_std = tax_std
    self.estm_stdprc = estm_stdprc
