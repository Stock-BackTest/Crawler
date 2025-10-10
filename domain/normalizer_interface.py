# domain/normalizer_interface.py
from typing import Protocol, Iterable, Dict, List


class Normalizer(Protocol):
  def normalize(
      self,
      records: Iterable[dict],
      mapping: Dict[str, List[str]],
  ) -> List[dict]:
    """
    records: Extractor가 반환한 원문 dict 리스트
    mapping: 표준필드 → 원문 키 후보 리스트
             예) {
               "pay_base_date": ["RGT_STD_DT", "STD_DT", "지급기준일"],
               "actual_pay_date": ["TH1_PAY_TERM_BEGIN_DT", "PAY_DT", "실지급일"],
               "div_type": ["RGT_RSN_DTAIL_NM", "DIV_TYPE", "배당구분"],
               "dist_per_share": ["BUNBE", "DIV_AMT_PER_SHR", "분배금"],
               "ticker": ["ISIN", "TICKER"]
             }
    context: 추가 주입값(예: {"ticker": "KR7...."}) — 레코드에서 못 찾으면 사용
    반환: 표준 스키마 dict 리스트
    """
    ...
