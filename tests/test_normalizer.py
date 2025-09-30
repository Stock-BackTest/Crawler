import unittest
from datetime import date

from infra.normalizer.default_normalizer import DefaultNormalizer
from domain.dividend_entity import DividendEntity

SAMPLE_RECORDS = [
    {
        "ISIN": "KR7276970001",
        "RGT_STD_DT": "20250924",
        "TH1_PAY_TERM_BEGIN_DT": "20250926",
        "BUNBE": "1.52833",
        "ESTM_STDPRC": "116",
        "RGT_RSN_DTAIL_NM": "이익분배",
    },
    {
        "ISIN": "KR7407170000",
        "RGT_STD_DT": "20250921",
        "TH1_PAY_TERM_BEGIN_DT": "20250922",
        "BUNBE": "",  # 빈 분배금 → 자동으로 0.0
        "ESTM_STDPRC": "9944.968864",
        "RGT_RSN_DTAIL_NM": "청산분배",
    },
]

MAPPING = {
    "isin":            ["ISIN"],
    "pay_base_date":   ["RGT_STD_DT"],
    "actual_pay_date": ["TH1_PAY_TERM_BEGIN_DT"],
    "div_type":        ["RGT_RSN_DTAIL_NM"],
    "dist_per_share":  ["BUNBE"],
    "estm_stdprc":     ["ESTM_STDPRC"],
}

class TestDefaultNormalizerEntity(unittest.TestCase):
    def test_normalize_returns_entities(self):
        normalizer = DefaultNormalizer()
        result = normalizer.normalize(SAMPLE_RECORDS, mapping=MAPPING)

        self.assertEqual(len(result), 2)

        ev1 = result[0]
        self.assertIsInstance(ev1, DividendEntity)
        self.assertEqual(ev1.isin, "KR7276970001")
        self.assertEqual(ev1.pay_base_date, date(2025, 9, 24))
        self.assertEqual(ev1.actual_pay_date, date(2025, 9, 26))
        self.assertEqual(ev1.div_type, "이익분배")
        self.assertAlmostEqual(ev1.dist_per_share, 1.52833, places=5)
        self.assertAlmostEqual(ev1.estm_stdprc, 116.0, places=5)

        ev2 = result[1]
        self.assertIsInstance(ev2, DividendEntity)
        self.assertEqual(ev2.isin, "KR7407170000")
        self.assertEqual(ev2.pay_base_date, date(2025, 9, 21))
        self.assertEqual(ev2.actual_pay_date, date(2025, 9, 22))
        self.assertEqual(ev2.div_type, "청산분배")
        self.assertAlmostEqual(ev2.dist_per_share, 0.0, places=6)
        self.assertAlmostEqual(ev2.estm_stdprc, 9944.968864, places=6)


if __name__ == "__main__":
    unittest.main()
