import datetime as dt
from dataclasses import dataclass, field
from typing import Mapping, Optional, Tuple

from domain.provider_interface import BaseProviderRequest
from infra.provider.seibro.requests.seibro_request import SeibroRequest


@dataclass
class OtherRequest(BaseProviderRequest):
  """supports() 음수 케이스 검증용 더미 요청 타입"""
  params: Mapping[str, str] = field(default_factory=dict)


def make_seibro_req(
    from_dt: Optional[dt.date] = None,
    to_dt: Optional[dt.date] = None,
    page: Optional[Tuple[int, int]] = None,
) -> SeibroRequest:
  """
  테스트에서 자주 쓰는 SeibroRequest 생성 헬퍼.
  - 날짜가 없으면 적당한 기본값 사용
  - page=(start, end) 튜플로 전달하면 .with_page_range 적용
  """
  if from_dt is None:
    from_dt = dt.date(2025, 9, 15)
  if to_dt is None:
    to_dt = dt.date(2025, 9, 21)

  req = SeibroRequest(from_dt=from_dt, to_dt=to_dt)
  if page is not None:
    req = req.with_page_range(*page)
  return req
