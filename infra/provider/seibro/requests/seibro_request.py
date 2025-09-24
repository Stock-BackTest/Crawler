from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field
from typing import Dict, Optional
from xml.etree.ElementTree import Element, SubElement, tostring

from domain.provider_interface import BaseProviderRequest


@dataclass
class SeibroRequest(BaseProviderRequest):
  action: str = "exerInfoDtramtPayStatPlist"
  task: str = "ksd.safe.bip.cnts.etf.process.EtfExerInfoPTask"
  w2xpath: str = "/IPORTAL/user/etf/BIP_CNTS06030V.xml"

  menu_no: str = "179"
  cmm_btn_abbr_nm: str = (
    "total_search,openall,print,hwp,word,pdf,searchIcon,searchIcon,"
    "seach,searchIcon,seach,"
  )

  start_page: str = "1"
  end_page: str = "1"
  from_dt: Optional[dt.date] = None
  to_dt: Optional[dt.date] = None

  # --- 검색/정렬 옵션(대부분 기본값/빈값) ---
  etf_sort_level_cd: str = "0"
  etf_big_sort_cd: str = ""
  etf_sort_cd: str = ""
  isin: str = ""
  mngco_custno: str = ""
  rgt_rsn_dtail_sort_cd: str = ""

  extra_params: Dict[str, str] = field(default_factory=dict)

  def __post_init__(self):
    if self.to_dt is None:
      self.to_dt = dt.date.today()
    if self.from_dt is None:
      self.from_dt = self.to_dt - dt.timedelta(days=365) - dt.timedelta(days=1)

    if self.from_dt > self.to_dt:
      self.from_dt, self.to_dt = self.to_dt, self.from_dt

    if not self.action or not self.task or not self.w2xpath:
      raise ValueError("action/task/w2xpath must be non-empty")
    if not self.menu_no:
      raise ValueError("menu_no must be non-empty")

  # ---------- 변환 유틸 ----------
  def as_params(self) -> Dict[str, str]:
    base = {
      "MENU_NO": self.menu_no,
      "CMM_BTN_ABBR_NM": self.cmm_btn_abbr_nm,
      "etf_sort_level_cd": self.etf_sort_level_cd,
      "etf_big_sort_cd": self.etf_big_sort_cd,
      "START_PAGE": str(self.start_page),
      "END_PAGE": str(self.end_page),
      "etf_sort_cd": self.etf_sort_cd,
      "isin": self.isin,
      "mngco_custno": self.mngco_custno,
      "RGT_RSN_DTAIL_SORT_CD": self.rgt_rsn_dtail_sort_cd,
      "fromRGT_STD_DT": self.from_dt.strftime("%Y%m%d"),
      "toRGT_STD_DT": self.to_dt.strftime("%Y%m%d"),
    }
    base.update(self.extra_params or {})
    return base

  def to_xml(self) -> str:
    params = self.as_params()

    root = Element("reqParam", action=self.action, task=self.task)

    if "MENU_NO" in params:
      SubElement(root, "MENU_NO", value=params["MENU_NO"])
    if "CMM_BTN_ABBR_NM" in params:
      SubElement(root, "CMM_BTN_ABBR_NM", value=params["CMM_BTN_ABBR_NM"])

    SubElement(root, "W2XPATH", value=self.w2xpath)

    for k, v in params.items():
      if k in ("MENU_NO", "CMM_BTN_ABBR_NM"):
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
