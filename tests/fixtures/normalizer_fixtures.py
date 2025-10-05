# tests/fixtures/normalizer_fixtures.py
from __future__ import annotations
from copy import deepcopy
from typing import Any, Dict, List

# --- 기본 케이스 ---
SAMPLE_RECORDS: List[Dict[str, Any]] = [
  {
    "ISIN": "KR7276970001",
    "RGT_STD_DT": "20250924",
    "TH1_PAY_TERM_BEGIN_DT": "20250926",
    "BUNBE": "1.52833",
    "ESTM_STDPRC": "116",
    "TAX_STD": "20352.73",
    "RGT_RSN_DTAIL_NM": "이익분배",
  },
  {
    "ISIN": "KR7407170000",
    "RGT_STD_DT": "20250921",
    "TH1_PAY_TERM_BEGIN_DT": "20250922",
    "BUNBE": "",  # 빈 분배금 → 0.0 기대
    "ESTM_STDPRC": "9944.968864",
    "TAX_STD": "1111.11",
    "RGT_RSN_DTAIL_NM": "청산분배",
  },
]

MAPPING: Dict[str, Any] = {
  "isin": ["ISIN"],
  "pay_base_date": ["RGT_STD_DT"],
  "actual_pay_date": ["TH1_PAY_TERM_BEGIN_DT"],
  "div_type": ["RGT_RSN_DTAIL_NM"],
  "dist_per_share": ["BUNBE"],
  "tax_std": ["TAX_STD"],
  "estm_stdprc": ["ESTM_STDPRC"],
}

# --- 대체 컬럼명 케이스 ---
SAMPLE_ALT = [
  {
    "ISIN_CODE": "KR7123450009",
    "BASE_DT": "20250115",
    "PAY_DT": "20250120",
    "DIV_KIND": "이익분배",
    "AMT_PER_SH": "2.5",
    "TAX_BASE": "10000.0",
    "ESTM_PRC": "123.45",
  }
]

MAPPING_ALT = {
  "isin": ["ISIN_CODE"],
  "pay_base_date": ["BASE_DT"],
  "actual_pay_date": ["PAY_DT"],
  "div_type": ["DIV_KIND"],
  "dist_per_share": ["AMT_PER_SH"],
  "tax_std": ["TAX_BASE"],
  "estm_stdprc": ["ESTM_PRC"],
}

# --- fallback 키 케이스 ---
SAMPLE_FALLBACK = [
  {
    "NEW_ISIN": "KR7999990000",
    "NEW_BASE": "20250301",
    "NEW_PAY": "20250305",
    "NEW_KIND": "청산분배",
    "NEW_AMT": "0.75",
    "NEW_TAX": "555.5",
    "NEW_PRC": "9876.5",
  },
  {
    "OLD_ISIN": "KR7888880001",
    "OLD_BASE": "20250302",
    "OLD_PAY": "20250306",
    "OLD_KIND": "이익분배",
    "OLD_AMT": "1.00",
    "OLD_TAX": "100.0",
    "OLD_PRC": "10.0",
  },
]

MAPPING_FALLBACK = {
  "isin": ["NEW_ISIN", "OLD_ISIN"],
  "pay_base_date": ["NEW_BASE", "OLD_BASE"],
  "actual_pay_date": ["NEW_PAY", "OLD_PAY"],
  "div_type": ["NEW_KIND", "OLD_KIND"],
  "dist_per_share": ["NEW_AMT", "OLD_AMT"],
  "tax_std": ["NEW_TAX", "OLD_TAX"],
  "estm_stdprc": ["NEW_PRC", "OLD_PRC"],
}

# --- 쉼표/공백 포함 숫자 케이스 ---
SAMPLE_COMMAS = [
  {
    "CODE": "KR7333330003",
    "BASE": "20250610",
    "PAY": "20250615",
    "KIND": "이익분배",
    "AMT": " 1,234.567 ",
    "TAX": "  2,000 ",
    "PRICE": " 9,999.99 ",
  }
]

MAPPING_COMMAS = {
  "isin": ["CODE"],
  "pay_base_date": ["BASE"],
  "actual_pay_date": ["PAY"],
  "div_type": ["KIND"],
  "dist_per_share": ["AMT"],
  "tax_std": ["TAX"],
  "estm_stdprc": ["PRICE"],
}

# --- optional 누락/빈 문자열 케이스 ---
SAMPLE_MISSING = [
  {
    "ISINX": "KR7444440004",
    "BASEX": "20250701",
    # "PAYX" 누락
    "KINDX": "이익분배",
    "AMTX": "",
    "TAXX": "10",
    "PRCX": "100",
  }
]

MAPPING_MISSING = {
  "isin": ["ISINX"],
  "pay_base_date": ["BASEX"],
  "actual_pay_date": ["PAYX"],  # 없으면 None 기대
  "div_type": ["KINDX"],
  "dist_per_share": ["AMTX"],
  "tax_std": ["TAXX"],
  "estm_stdprc": ["PRCX"],
}

# --- 빈 입력용 매핑 ---
EMPTY_INPUT_MAPPING = {
  "isin": ["X1"],
  "pay_base_date": ["X2"],
  "actual_pay_date": ["X3"],
  "div_type": ["X4"],
  "dist_per_share": ["X5"],
  "tax_std": ["X6"],
  "estm_stdprc": ["X7"],
}

# --- 안전한 사용을 위한 helper(깊은 복사) ---
def copy_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
  return deepcopy(records)

def copy_mapping(mapping: Dict[str, Any]) -> Dict[str, Any]:
  return deepcopy(mapping)
