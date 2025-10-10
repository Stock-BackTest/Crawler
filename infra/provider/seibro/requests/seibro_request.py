from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

from domain.provider_interface import BaseProviderRequest
from infra.provider.seibro import constants as C


@dataclass
class SeibroRequest(BaseProviderRequest):
  # 기본 동작/경로
  action: str = C.DEFAULT_ACTION
  task: str = C.DEFAULT_TASK
  w2xpath: str = C.DEFAULT_W2XPATH

  # 공통 파라미터
  menu_no: str = C.DEFAULT_MENU_NO
  cmm_btn_abbr_nm: str = C.DEFAULT_CMM_BTN_ABBR_NM

  # 페이지/기간
  start_page: str = C.DEFAULT_START_PAGE
  end_page: str = C.DEFAULT_END_PAGE
  from_dt: Optional[dt.date] = None
  to_dt: Optional[dt.date] = None

  # 검색/정렬 옵션
  etf_sort_level_cd: str = C.DEFAULT_ETF_SORT_LEVEL_CD
  etf_big_sort_cd: str = C.DEFAULT_ETF_BIG_SORT_CD
  etf_sort_cd: str = C.DEFAULT_ETF_SORT_CD
  isin: str = C.DEFAULT_ISIN
  mngco_custno: str = C.DEFAULT_MNGCO_CUSTNO
  rgt_rsn_dtail_sort_cd: str = C.DEFAULT_RGT_RSN_DTAIL_SORT_CD

  extra_params: Dict[str, str] = field(default_factory=dict)

  def __post_init__(self):
    if self.to_dt is None:
      self.to_dt = dt.date.today()
    if self.from_dt is None:
      self.from_dt = self.to_dt - dt.timedelta(days=366)

    if self.from_dt > self.to_dt:
      self.from_dt, self.to_dt = self.to_dt, self.from_dt

    if not self.action or not self.task or not self.w2xpath:
      raise ValueError("action/task/w2xpath must be non-empty")
    if not self.menu_no:
      raise ValueError("menu_no must be non-empty")

  # ---------- 변환 유틸 ----------
  def as_params(self) -> Dict[str, str]:
    base = {
      C.K_MENU_NO: self.menu_no,
      C.K_CMM_BTN_ABBR_NM: self.cmm_btn_abbr_nm,
      C.K_ETF_SORT_LEVEL_CD: self.etf_sort_level_cd,
      C.K_ETF_BIG_SORT_CD: self.etf_big_sort_cd,
      C.K_START_PAGE: str(self.start_page),
      C.K_END_PAGE: str(self.end_page),
      C.K_ETF_SORT_CD: self.etf_sort_cd,
      C.K_ISIN: self.isin,
      C.K_MNGCO_CUSTNO: self.mngco_custno,
      C.K_RGT_RSN_DTAIL_SORT_CD: self.rgt_rsn_dtail_sort_cd,
      C.K_FROM_DT: self.from_dt.strftime(C.DATE_FMT),
      C.K_TO_DT: self.to_dt.strftime(C.DATE_FMT),
    }
    base.update(self.extra_params or {})
    return base

  def to_xml(self) -> str:
    params = self.as_params()

    root = Element("reqParam", action=self.action, task=self.task)

    if C.K_MENU_NO in params:
      SubElement(root, C.K_MENU_NO, value=params[C.K_MENU_NO])
    if C.K_CMM_BTN_ABBR_NM in params:
      SubElement(root, C.K_CMM_BTN_ABBR_NM, value=params[C.K_CMM_BTN_ABBR_NM])

    SubElement(root, C.K_W2XPATH, value=self.w2xpath)

    for k, v in params.items():
      if k in (C.K_MENU_NO, C.K_CMM_BTN_ABBR_NM):
        continue
      SubElement(root, k, value=("" if v is None else str(v)))

    return tostring(root, encoding="utf-8", method="xml").decode("utf-8")

  def with_page(self, page: int) -> "SeibroRequest":
    return SeibroRequest(
        **{**self.__dict__, "start_page": str(page), "end_page": str(page)}
    )

  def with_page_range(self, start: int, end: int) -> "SeibroRequest":
    return SeibroRequest(
        **{**self.__dict__, "start_page": str(start), "end_page": str(end)}
    )

  def with_date_range(self, start: dt.date, end: dt.date) -> "SeibroRequest":
    return SeibroRequest(
        **{**self.__dict__, "from_dt": start, "to_dt": end}
    )
