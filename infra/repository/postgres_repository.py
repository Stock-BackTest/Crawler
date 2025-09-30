from __future__ import annotations
from typing import List, Optional, Dict, Iterable, Any

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.dialects.postgresql import insert as pg_insert

from domain.dividend_entity import Base, DividendEntity
from domain.repository_interface import DividendRepository


class PostgresDividendRepository(DividendRepository):
    """
    - 테이블이 없으면 자동 생성
    - save(): PostgreSQL upsert(ON CONFLICT)로 배치 저장
    - load(): 단순 equal 조건 dict로 조회
    """

    def __init__(self, url: str, echo: bool = False):
        """
        url 예:
          - postgresql+psycopg://user:pass@localhost:5432/dbname   (psycopg3)
          - postgresql+psycopg2://user:pass@localhost:5432/dbname (psycopg2)
        """
        self.engine: Engine = create_engine(url, echo=echo, future=True)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(self.engine, expire_on_commit=False, class_=Session)

    def save(self, records: List[DividendEntity]) -> None:
        if not records:
            return
        self._upsert(records)

    def load(self, query: Optional[Dict[str, Any]] = None) -> List[DividendEntity]:
        with self.SessionLocal() as sess:
            stmt = select(DividendEntity)
            if query:
                for k, v in query.items():
                    col = getattr(DividendEntity, k)
                    stmt = stmt.where(col == v)
            rows = sess.execute(stmt).scalars().all()
            return rows

    def _upsert(self, records: Iterable[DividendEntity], chunk_size: int = 1000) -> None:
        def chunker(it: Iterable[DividendEntity], n: int):
            buf = []
            for x in it:
                buf.append(x)
                if len(buf) >= n:
                    yield buf
                    buf = []
            if buf:
                yield buf

        with self.SessionLocal() as sess:
            for batch in chunker(records, chunk_size):
                values = [
                    {
                        "isin": r.isin,
                        "pay_base_date": r.pay_base_date,
                        "actual_pay_date": r.actual_pay_date,
                        "div_type": r.div_type,
                        "dist_per_share": r.dist_per_share,
                        "estm_stdprc": r.estm_stdprc,
                    }
                    for r in batch
                ]
                stmt = pg_insert(DividendEntity).values(values)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["isin", "pay_base_date"],
                    set_={
                        "actual_pay_date": stmt.excluded.actual_pay_date,
                        "div_type": stmt.excluded.div_type,
                        "dist_per_share": stmt.excluded.dist_per_share,
                        "estm_stdprc": stmt.excluded.estm_stdprc,
                    },
                )
                sess.execute(stmt)
            sess.commit()
