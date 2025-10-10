import os
import unittest
from typing import Sequence

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import class_mapper

from domain.dividend_entity import Base, DividendEntity
from infra.repository.postgres_repository import PostgresDividendRepository

try:
    load_dotenv()
except Exception:
    pass


class DBCleaner(unittest.TestCase):
    TABLES: Sequence[str] = ("dividends",)
    TRUNCATE_CASCADE: bool = False
    RESTART_IDENTITY: bool = True

    @classmethod
    def setUpClass(cls):
        cls.url = os.getenv("TEST_POSTGRES_URL")
        if not cls.url:
            raise unittest.SkipTest(
                "TEST POSTGRES_URL not set; skipping PG integration tests."
            )

        # 1) Engine
        cls.engine: Engine = create_engine(cls.url, future=True)

        # 2) 스키마 초기화: 테스트는 무조건 깨끗하게 시작
        with cls.engine.begin() as conn:
            for t in cls.TABLES:
                conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE;"))

        # 3) 최신 엔티티 기준 재생성
        Base.metadata.create_all(cls.engine)

        # 4) 스키마 검증 (엔티티 ↔ DB)
        insp = inspect(cls.engine)
        db_cols = {c["name"] for c in insp.get_columns("dividends")}
        entity_cols = {col.key for col in class_mapper(DividendEntity).columns}

        missing = entity_cols - db_cols
        extra = db_cols - entity_cols
        assert not missing, f"Schema invalid after recreate: missing → {missing}"
        if extra:
            print(f"[WARN] Extra columns in DB but not in entity: {extra}")

        # 5) Repo (엔진 주입)
        cls.repo = PostgresDividendRepository(engine=cls.engine, echo=False)

    def setUp(self):
        # 매 테스트마다 데이터만 초기화
        opts = []
        if self.RESTART_IDENTITY:
            opts.append("RESTART IDENTITY")
        if self.TRUNCATE_CASCADE:
            opts.append("CASCADE")
        suffix = f" {' '.join(opts)}" if opts else ""

        with self.engine.begin() as conn:
            for t in self.TABLES:
                conn.execute(text(f"TRUNCATE TABLE {t}{suffix};"))

    # 유틸
    def count(self, table: str = "dividends") -> int:
        with self.engine.begin() as conn:
            return conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
