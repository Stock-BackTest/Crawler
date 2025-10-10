import unittest
from datetime import date

from domain.dividend_entity import DividendEntity
from infra.normalizer.default_normalizer import DefaultNormalizer

from tests.common.fixtures.normalizer_fixtures import (
  SAMPLE_RECORDS, MAPPING,
  SAMPLE_ALT, MAPPING_ALT,
  SAMPLE_FALLBACK, MAPPING_FALLBACK,
  SAMPLE_COMMAS, MAPPING_COMMAS,
  SAMPLE_MISSING, MAPPING_MISSING,
  EMPTY_INPUT_MAPPING,
  copy_records, copy_mapping,
)


class TestDefaultNormalizerEntity(unittest.TestCase):
  def test_normalize_returns_entities(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize(
      copy_records(SAMPLE_RECORDS),
      mapping=copy_mapping(MAPPING),
    )

    self.assertEqual(len(result), 2)

    ev1 = result[0]
    self.assertIsInstance(ev1, DividendEntity)
    self.assertEqual(ev1.isin, "KR7276970001")
    self.assertEqual(ev1.pay_base_date, date(2025, 9, 24))
    self.assertEqual(ev1.actual_pay_date, date(2025, 9, 26))
    self.assertEqual(ev1.div_type, "이익분배")
    self.assertAlmostEqual(ev1.dist_per_share, 1.52833, places=5)
    self.assertAlmostEqual(ev1.tax_std, 20352.73, places=5)
    self.assertAlmostEqual(ev1.estm_stdprc, 116.0, places=5)

    ev2 = result[1]
    self.assertIsInstance(ev2, DividendEntity)
    self.assertEqual(ev2.isin, "KR7407170000")
    self.assertEqual(ev2.pay_base_date, date(2025, 9, 21))
    self.assertEqual(ev2.actual_pay_date, date(2025, 9, 22))
    self.assertEqual(ev2.div_type, "청산분배")
    self.assertAlmostEqual(ev2.dist_per_share, 0.0, places=6)
    self.assertAlmostEqual(ev2.tax_std, 1111.11, places=5)
    self.assertAlmostEqual(ev2.estm_stdprc, 9944.968864, places=6)

  def test_normalize_alt_columns_simple(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize(
      copy_records(SAMPLE_ALT),
      mapping=copy_mapping(MAPPING_ALT),
    )
    self.assertEqual(len(result), 1)

    ev = result[0]
    self.assertIsInstance(ev, DividendEntity)
    self.assertEqual(ev.isin, "KR7123450009")
    self.assertEqual(ev.pay_base_date, date(2025, 1, 15))
    self.assertEqual(ev.actual_pay_date, date(2025, 1, 20))
    self.assertEqual(ev.div_type, "이익분배")
    self.assertAlmostEqual(ev.dist_per_share, 2.5, places=6)
    self.assertAlmostEqual(ev.tax_std, 10000.0, places=6)
    self.assertAlmostEqual(ev.estm_stdprc, 123.45, places=6)

  def test_normalize_alt_columns_with_fallback_keys(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize(
      copy_records(SAMPLE_FALLBACK),
      mapping=copy_mapping(MAPPING_FALLBACK),
    )
    self.assertEqual(len(result), 2)

    a, b = result
    self.assertEqual(a.isin, "KR7999990000")
    self.assertEqual(a.pay_base_date, date(2025, 3, 1))
    self.assertEqual(a.actual_pay_date, date(2025, 3, 5))
    self.assertEqual(a.div_type, "청산분배")
    self.assertAlmostEqual(a.dist_per_share, 0.75, places=6)
    self.assertAlmostEqual(a.tax_std, 555.5, places=6)
    self.assertAlmostEqual(a.estm_stdprc, 9876.5, places=6)

    self.assertEqual(b.isin, "KR7888880001")
    self.assertEqual(b.pay_base_date, date(2025, 3, 2))
    self.assertEqual(b.actual_pay_date, date(2025, 3, 6))
    self.assertEqual(b.div_type, "이익분배")
    self.assertAlmostEqual(b.dist_per_share, 1.0, places=6)
    self.assertAlmostEqual(b.tax_std, 100.0, places=6)
    self.assertAlmostEqual(b.estm_stdprc, 10.0, places=6)

  def test_normalize_alt_columns_with_commas_and_spaces(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize(
      copy_records(SAMPLE_COMMAS),
      mapping=copy_mapping(MAPPING_COMMAS),
    )
    self.assertEqual(len(result), 1)
    ev = result[0]
    self.assertEqual(ev.isin, "KR7333330003")
    self.assertEqual(ev.pay_base_date, date(2025, 6, 10))
    self.assertEqual(ev.actual_pay_date, date(2025, 6, 15))
    self.assertEqual(ev.div_type, "이익분배")
    self.assertAlmostEqual(ev.dist_per_share, 1234.567, places=6)
    self.assertAlmostEqual(ev.tax_std, 2000.0, places=6)
    self.assertAlmostEqual(ev.estm_stdprc, 9999.99, places=6)

  def test_normalize_alt_columns_with_missing_optional_fields(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize(
      copy_records(SAMPLE_MISSING),
      mapping=copy_mapping(MAPPING_MISSING),
    )
    self.assertEqual(len(result), 1)
    ev = result[0]
    self.assertEqual(ev.isin, "KR7444440004")
    self.assertEqual(ev.pay_base_date, date(2025, 7, 1))
    self.assertIsNone(ev.actual_pay_date)
    self.assertEqual(ev.div_type, "이익분배")
    self.assertAlmostEqual(ev.dist_per_share, 0.0, places=6)
    self.assertAlmostEqual(ev.tax_std, 10.0, places=6)
    self.assertAlmostEqual(ev.estm_stdprc, 100.0, places=6)

  def test_normalize_empty_input(self):
    normalizer = DefaultNormalizer()
    result = normalizer.normalize([], mapping=copy_mapping(EMPTY_INPUT_MAPPING))
    self.assertEqual(result, [])


if __name__ == "__main__":
  unittest.main()
