import unittest
from infra.normalizer.default_normalizer import DefaultNormalizer

SAMPLE_RECORDS = [
    {
        "ISIN": "KR7276970001",
        "KOR_SECN_NM": "KODEX 미국S&P500배당귀족커버드콜(합성 H)",
        "ETF_SORT_CD": "P0301",
        "ISSUCO_CUSTNO": "216516",
        "RGT_STD_DT": "20250924",
        "TH1_PAY_TERM_BEGIN_DT": "20250926",
        "ESTM_STDPRC": "116",
        "BUNBE": "1.52833",
        "ETF_SORT_NM": "파생상품/구조화",
        "REP_SECN_NM": "삼성자산운용",
        "TAXSTD": "9504.15",
        "RGT_RSN_DTAIL_NM": "이익분배",
    },
    {
        "ISIN": "KR7407170000",
        "KOR_SECN_NM": "KCGI 스마트커머스액티브",
        "ETF_SORT_CD": "M0901",
        "ISSUCO_CUSTNO": "248998",
        "RGT_STD_DT": "20250921",
        "TH1_PAY_TERM_BEGIN_DT": "20250922",
        "ESTM_STDPRC": "9944.968864",
        "BUNBE": "",
        "ETF_SORT_NM": "테마/기타",
        "REP_SECN_NM": "케이씨지아이자산운용",
        "TAXSTD": "10626.34728",
        "RGT_RSN_DTAIL_NM": "청산분배",
    },
]

MAPPING = {
    "isin": ["ISIN"],
    "pay_base_date": ["RGT_STD_DT"],
    "actual_pay_date": ["TH1_PAY_TERM_BEGIN_DT"],
    "div_type": ["RGT_RSN_DTAIL_NM"],
    "dist_per_share": ["BUNBE"],
    "estm_stdprc": ["ESTM_STDPRC"],
}

class TestDefaultNormalizer(unittest.TestCase):
    def test_normalize(self):
        normalizer = DefaultNormalizer()
        result = normalizer.normalize(SAMPLE_RECORDS, mapping=MAPPING)

        self.assertEqual(len(result), 1)

        record = result[0]
        self.assertEqual(record["isin"], "KR7276970001")
        self.assertEqual(record["pay_base_date"], "2025-09-24")
        self.assertEqual(record["actual_pay_date"], "2025-09-26")
        self.assertEqual(record["div_type"], "이익분배")
        self.assertEqual(record["dist_per_share"], "1.52833")
        self.assertEqual(record["estm_stdprc"], "116")

    def test_strict_false(self):
        normalizer = DefaultNormalizer(strict=False)
        result = normalizer.normalize(SAMPLE_RECORDS, mapping=MAPPING)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["isin"], "KR7407170000")
        self.assertEqual(result[1]["dist_per_share"], "")

if __name__ == "__main__":
    unittest.main()
