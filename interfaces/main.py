from __future__ import annotations

import argparse
import os

from app.crawler_service import CrawlerService
from infra.extractor.xml_extractor import XmlDividendExtractor
from infra.normalizer.default_normalizer import DefaultDividendNormalizer
from infra.provider.seibro.seibro_provider import SeibroDividendProvider
from infra.repository.postgres_repository import PostgresDividendRepository
from interfaces.request.crawler_request import CrawlerRequest


def make_parser() -> argparse.ArgumentParser:
  p = argparse.ArgumentParser(description="Dividend Crawler CLI")
  p.add_argument("--provider", required=True)
  p.add_argument("--from-dt")
  p.add_argument("--to-dt")
  p.add_argument("--max-page", type=int)
  p.add_argument("--size", type=int)
  return p


def make_service() -> CrawlerService:
  url = os.getenv("DATABASE_URL")
  if not url:
    raise ValueError(
        "DATABASE_URL not set; skipping PG integration tests.")

  providers = [SeibroDividendProvider()]
  extractors = [XmlDividendExtractor()]
  normalizer = DefaultDividendNormalizer()
  repository = PostgresDividendRepository(url=url)

  svc = CrawlerService(
      providers=providers,
      extractors=extractors,
      normalizer=normalizer,
      repository=repository,
  )
  return svc


def main():
  parser = make_parser()

  ns = parser.parse_args()
  req = CrawlerRequest.from_cli(ns)

  svc = make_service()

  svc.execute(request=req)


if __name__ == "__main__":
  main()
