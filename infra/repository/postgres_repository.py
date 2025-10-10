from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

from sqlalchemy import create_engine, select, literal_column
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session, sessionmaker

from domain.dividend_entity import Base, DividendEntity
from domain.repository_interface import DividendRepository


class PostgresDividendRepository(DividendRepository):
  def __init__(
      self,
      url: Optional[str] = None,
      engine: Optional[Engine] = None,
      echo: bool = False,
  ) -> None:
    if not (url or engine):
      raise ValueError("Either 'url' or 'engine' must be provided.")

    self.engine: Engine = engine or create_engine(url, echo=echo, future=True)
    Base.metadata.create_all(self.engine)

    self.SessionLocal = sessionmaker(
        bind=self.engine,
        class_=Session,
        expire_on_commit=False,
        future=True,
    )

    # 복합 충돌키 (PK)
    self._conflict_cols: Sequence[str] = ("isin", "pay_base_date")

    # 모델 컬럼 메타 (테이블 컬럼 이름 집합)
    self._model_cols: set[str] = {c.key for c in
                                  inspect(DividendEntity).mapper.columns}

    # UPSERT 시 갱신 대상 컬럼
    self._updatable_cols: tuple[str, ...] = tuple(
        c for c in self._model_cols if c not in self._conflict_cols
    )

  # ---------- session helper ----------
  @contextmanager
  def session(self) -> Iterator[Session]:
    sess = self.SessionLocal()
    try:
      yield sess
      sess.commit()
    except Exception:
      sess.rollback()
      raise
    finally:
      sess.close()

  # ---------- public APIs ----------
  def save(self, records: List[DividendEntity]) -> int:
    if not records:
      return 0
    return self.bulk_upsert(records)

  def load(
      self,
      query: Optional[Dict[str, Any]] = None,
      *,
      order_by: Optional[Sequence[str]] = None,
      limit: Optional[int] = None,
      offset: Optional[int] = None,
  ) -> List[DividendEntity]:
    """
    - order_by: ["isin", "-pay_base_date"]  # '-' 접두어는 DESC
    """
    with self.session() as sess:
      stmt = select(DividendEntity)

      if query:
        # 존재하지 않는 컬럼 키가 들어오면 명시적으로 에러
        invalid = set(query.keys()) - self._model_cols
        if invalid:
          raise AttributeError(f"Unknown columns in query: {invalid}")

        for k, v in query.items():
          stmt = stmt.where(getattr(DividendEntity, k) == v)

      if order_by:
        orders = []
        for name in order_by:
          descending = name.startswith("-")
          colname = name[1:] if descending else name
          if colname not in self._model_cols:
            raise AttributeError(f"Unknown column in order_by: {colname}")
          col = getattr(DividendEntity, colname)
          orders.append(col.desc() if descending else col.asc())
        if orders:
          stmt = stmt.order_by(*orders)

      if limit is not None:
        stmt = stmt.limit(limit)
      if offset is not None:
        stmt = stmt.offset(offset)

      return sess.execute(stmt).scalars().all()

  def bulk_upsert(
      self,
      records: Iterable[DividendEntity],
      *,
      chunk_size: int = 1000,
  ) -> int:
    total_affected = 0

    with self.session() as sess:
      for batch in self._chunked(records, chunk_size):
        values = [self._to_values(r) for r in batch]

        stmt = pg_insert(DividendEntity.__table__).values(values)

        update_map = {c: getattr(stmt.excluded, c) for c in
                      self._updatable_cols}

        stmt = (
          stmt.on_conflict_do_update(
              index_elements=list(self._conflict_cols),
              set_=update_map,
          )
          .returning(literal_column("1"))
        )

        result = sess.execute(stmt)
        total_affected += len(result.fetchall())

    return total_affected

  # ---------- utils ----------
  def _to_values(self, r: DividendEntity) -> Dict[str, Any]:
    return {
      "isin": r.isin,
      "pay_base_date": r.pay_base_date,
      "actual_pay_date": r.actual_pay_date,
      "div_type": r.div_type,
      "dist_per_share": r.dist_per_share,
      "tax_std": r.tax_std,
      "estm_stdprc": r.estm_stdprc,
    }

  @staticmethod
  def _chunked(it: Iterable[DividendEntity], n: int) -> Iterable[
    List[DividendEntity]]:
    buf: List[DividendEntity] = []
    for x in it:
      buf.append(x)
      if len(buf) >= n:
        yield buf
        buf = []
    if buf:
      yield buf
