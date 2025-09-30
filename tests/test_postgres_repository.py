import os
import unittest
from datetime import date

from sqlalchemy import create_engine, text

from domain.dividend_entity import DividendEntity
from infra.repository.postgres_repository import PostgresDividendRepository
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    pass


class TestPostgresDividendRepository(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
        if not cls.url:
            raise unittest.SkipTest("DATABASE_URL (or POSTGRES_URL) not set; skipping PG integration test.")

        print(cls.url)
        # 리포지토리 생성 (테이블 자동 생성)
        cls.repo = PostgresDividendRepository(url=cls.url, echo=False)

        # 테스트 전에 테이블 비우기
        engine = create_engine(cls.url, future=True)
        with engine.begin() as conn:
            conn.execute(text("DELETE FROM dividends"))

    def test_save_and_load(self):
        # Given
        entities = [
            DividendEntity(
                isin="KR7276970001",
                pay_base_date=date(2025, 9, 24),
                actual_pay_date=date(2025, 9, 26),
                div_type="이익분배",
                dist_per_share=1.52833,
                estm_stdprc=116.0,
            ),
            DividendEntity(
                isin="KR7407170000",
                pay_base_date=date(2025, 9, 21),
                actual_pay_date=date(2025, 9, 22),
                div_type="청산분배",
                dist_per_share=0.0,
                estm_stdprc=9944.968864,
            ),
        ]

        # When: 저장
        self.repo.save(entities)

        # Then: 조회 (전체)
        all_rows = self.repo.load()
        self.assertEqual(len(all_rows), 2)

        # 특정 ISIN 조회
        rows1 = self.repo.load({"isin": "KR7276970001"})
        self.assertEqual(len(rows1), 1)
        r1 = rows1[0]
        self.assertEqual(r1.isin, "KR7276970001")
        self.assertEqual(r1.pay_base_date, date(2025, 9, 24))
        self.assertEqual(r1.actual_pay_date, date(2025, 9, 26))
        self.assertEqual(r1.div_type, "이익분배")
        self.assertAlmostEqual(r1.dist_per_share, 1.52833, places=5)
        self.assertAlmostEqual(r1.estm_stdprc, 116.0, places=5)

        # UPSERT 동작 검증: 동일 (isin, pay_base_date)로 값 변경 저장
        updated = DividendEntity(
            isin="KR7276970001",
            pay_base_date=date(2025, 9, 24),
            actual_pay_date=date(2025, 9, 27),  # 날짜 변경
            div_type="이익분배",
            dist_per_share=1.6,                 # 금액 변경
            estm_stdprc=120.0,                 # 기준가 변경
        )
        self.repo.save([updated])

        rows1b = self.repo.load({"isin": "KR7276970001"})
        self.assertEqual(len(rows1b), 1)
        r1b = rows1b[0]
        self.assertEqual(r1b.actual_pay_date, date(2025, 9, 27))
        self.assertAlmostEqual(r1b.dist_per_share, 1.6, places=6)
        self.assertAlmostEqual(r1b.estm_stdprc, 120.0, places=6)


if __name__ == "__main__":
    unittest.main()
