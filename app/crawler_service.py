import datetime as dt
from typing import List, Dict

from domain.extractor_interface import DividendExtractor, RawResponse
from domain.normalizer_interface import DividendNormalizer
from domain.provider_interface import DividendProvider, BaseProviderRequest
from domain.repository_interface import DividendRepository
from infra.provider.seibro.constants import PROVIDER_SEIBRO, \
  SEIBRO_FIELD_MAPPING
from infra.provider.seibro.requests.seibro_request import SeibroRequest
from interfaces.request.crawler_request import CrawlerRequest


def _to_req(
    provider: str,
    page: int,
    size: int,
    from_dt: dt.date,
    to_dt: dt.date) -> BaseProviderRequest | None:
  if provider.lower() == PROVIDER_SEIBRO:
    start = (page - 1) * size + 1
    end = page * size
    return (SeibroRequest()
            .with_date_range(start=from_dt, end=to_dt)
            .with_page_range(start=start, end=end))
  return None


def _get_mapping(provider: str) -> Dict[str, List[str]] | None:
  if provider.lower() == PROVIDER_SEIBRO:
    return SEIBRO_FIELD_MAPPING
  return None


class CrawlerService:
  def __init__(self,
      providers: List[DividendProvider],
      extractors: List[DividendExtractor],
      normalizer: DividendNormalizer,
      repository: DividendRepository
  ):
    self.providers = providers
    self.extractors = extractors
    self.normalizer = normalizer
    self.repository = repository

  def execute(self, request: CrawlerRequest):
    for page in range(1, request.max_page + 1):
      req = _to_req(
          provider=request.provider,
          from_dt=request.from_dt,
          to_dt=request.to_dt,
          page=page,
          size=request.size
      )
      if req is None:
        raise ValueError(f"Invalid provider: {request.provider}")

      provider = next((p for p in self.providers if p.supports(req)), None)
      if provider is None:
        raise ValueError(f"No provider can handle: {type(req).__name__}")
      resp = provider.fetch(req=req)

      raw = RawResponse.convert(resp=resp)
      extractor = next((e for e in self.extractors if e.can_handle(raw)), None)
      if extractor is None:
        raise ValueError(f"No extractor can handle: {type(req).__name__}")
      rows = extractor.parse(raw=raw)

      mapping = _get_mapping(request.provider)
      if mapping is None:
        raise ValueError(f"Invalid provider: {provider}")

      records = self.normalizer.normalize(records=rows, mapping=mapping)

      if len(records) < request.size:
        break

      self.repository.save(records=records)
