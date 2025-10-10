import unittest
from datetime import date
from sqlalchemy.exc import IntegrityError, DataError

from tests.common.db_cleaner import DBCleaner
from tests.common.fixtures.dividends_fixtures import (
    sample_pair,
    updated_for_upsert,
    make_dividend,
    div_type_exact_len,
    div_type_too_long,
)


class TestPostgresDividendRepository(DBCleaner):

    # ---------- Save (insert only) ----------
    def test_save_inserts(self):
        # Given
        records = sample_pair()

        # When
        self.repo.save(records)

        # Then
        self.assertEqual(self.count(), 2)
        rows = self.repo.load({"isin": "KR7276970001"})
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r.pay_base_date, date(2025, 9, 24))
        self.assertEqual(r.actual_pay_date, date(2025, 9, 26))
        self.assertAlmostEqual(r.dist_per_share, 1.52833, places=5)
        self.assertAlmostEqual(r.tax_std, 1111.11, places=2)
        self.assertAlmostEqual(r.estm_stdprc, 116.0, places=5)

    # ---------- Upsert (update existing) ----------
    def test_upsert_updates(self):
        # Given: 먼저 원본 1건 삽입
        base = make_dividend(
            isin="KR7276970001",
            pay_base_date=date(2025, 9, 24),
            actual_pay_date=date(2025, 9, 26),
            div_type="이익분배",
            dist_per_share=1.52833,
            tax_std=1111.11,
            estm_stdprc=116.0,
        )
        self.repo.save([base])
        self.assertEqual(self.count(), 1)

        # When: 동일 PK로 값 변경(upsert)
        self.repo.save([updated_for_upsert()])

        # Then: 행 수 유지 + 변경 반영 확인
        self.assertEqual(self.count(), 1)
        rows = self.repo.load({"isin": "KR7276970001"})
        self.assertEqual(len(rows), 1)
        r = rows[0]
        self.assertEqual(r.actual_pay_date, date(2025, 9, 27))
        self.assertAlmostEqual(r.dist_per_share, 1.6, places=6)
        self.assertAlmostEqual(r.tax_std, 2222.22, places=6)
        self.assertAlmostEqual(r.estm_stdprc, 120.0, places=6)

    # ---------- Load ----------
    def test_load_all_and_filters_and_ordering(self):
        # Given
        a = make_dividend(
            isin="AAA000000000",
            pay_base_date=date(2025, 1, 1),
            actual_pay_date=None,
            div_type="TYPE",
            dist_per_share=0.0,
            tax_std=0.0,
            estm_stdprc=1.0,
        )
        b = make_dividend(
            isin="BBB000000000",
            pay_base_date=date(2025, 1, 2),
            actual_pay_date=date(2025, 1, 3),
            div_type="TYPE",
            dist_per_share=2.5,
            tax_std=10.0,
            estm_stdprc=100.0,
        )
        c = make_dividend(
            isin="BBB000000000",
            pay_base_date=date(2025, 1, 1),
            actual_pay_date=date(2025, 1, 2),
            div_type="TYPE",
            dist_per_share=1.0,
            tax_std=5.0,
            estm_stdprc=50.0,
        )
        self.repo.save([a, b, c])

        # all
        all_rows = self.repo.load()
        self.assertEqual(len(all_rows), 3)

        # filter by isin
        rows_bbb = self.repo.load({"isin": "BBB000000000"})
        self.assertEqual(len(rows_bbb), 2)

        # combo filter
        row_specific = self.repo.load(
            {"isin": "BBB000000000", "pay_base_date": date(2025, 1, 1)}
        )
        self.assertEqual(len(row_specific), 1)
        self.assertEqual(row_specific[0].actual_pay_date, date(2025, 1, 2))

        # ordering desc
        rows_ordered = self.repo.load({"isin": "BBB000000000"}, order_by=["-pay_base_date"])
        self.assertEqual(rows_ordered[0].pay_base_date, date(2025, 1, 2))
        self.assertEqual(rows_ordered[1].pay_base_date, date(2025, 1, 1))

        # pagination
        page1 = self.repo.load(order_by=["isin", "pay_base_date"], limit=2, offset=0)
        page2 = self.repo.load(order_by=["isin", "pay_base_date"], limit=2, offset=2)
        self.assertEqual(len(page1), 2)
        self.assertEqual(len(page2), 1)

    # ---------- Boundary ----------
    def test_boundary_empty_save_is_noop(self):
        affected = self.repo.save([])
        self.assertEqual(affected, 0)
        self.assertEqual(self.count(), 0)

    def test_boundary_div_type_exact_50(self):
        e = make_dividend(
            isin="LEN50",
            pay_base_date=date(2025, 1, 1),
            actual_pay_date=None,
            div_type=div_type_exact_len(),
            dist_per_share=0.0,
            tax_std=0.0,
            estm_stdprc=0.0,
        )
        self.repo.save([e])
        rows = self.repo.load({"isin": "LEN50"})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].div_type, div_type_exact_len())

    # ---------- Negative ----------
    def test_negative_load_with_unknown_column_raises(self):
        with self.assertRaises(AttributeError):
            self.repo.load({"unknown_column": "value"})

    def test_negative_not_null_violation(self):
        bad = make_dividend(
            isin="NNV001",
            pay_base_date=date(2025, 1, 1),
            actual_pay_date=None,
            div_type="TYPE",
            dist_per_share=None,  # type: ignore
            tax_std=0.0,
            estm_stdprc=0.0,
        )
        with self.assertRaises((IntegrityError, DataError)):
            self.repo.save([bad])

    def test_negative_div_type_length_exceeded(self):
        bad = make_dividend(
            isin="LONG51",
            pay_base_date=date(2025, 1, 1),
            actual_pay_date=None,
            div_type=div_type_too_long(),
            dist_per_share=0.0,
            tax_std=0.0,
            estm_stdprc=0.0,
        )
        with self.assertRaises(DataError):
            self.repo.save([bad])


if __name__ == "__main__":
    unittest.main(verbosity=2)
