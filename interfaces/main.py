from __future__ import annotations

import argparse
import logging
import os
import sys

from app.crawler_service import CrawlerService
from infra.extractor.xml_extractor import XmlDividendExtractor
from infra.normalizer.default_normalizer import DefaultDividendNormalizer
from infra.provider.seibro.seibro_provider import SeibroDividendProvider
from infra.repository.postgres_repository import PostgresDividendRepository
from interfaces.request.crawler_request import CrawlerRequest


def configure_logging(level_str: str):
  level = getattr(logging, level_str.upper(), logging.INFO)
  logging.info("Logger configured: level=%s", level)
  logging.basicConfig(
      level=level,
      format="%(asctime)s [%(levelname)s] %(message)s",
      force=True,
  )


def make_parser() -> argparse.ArgumentParser:
  logging.info("Make argument parser")
  p = argparse.ArgumentParser(description="Dividend Crawler CLI")
  p.add_argument("--provider", default=os.getenv("CRAWLER_PROVIDER"))
  p.add_argument("--from-dt", default=os.getenv("CRAWLER_FROM"))
  p.add_argument("--to-dt", default=os.getenv("CRAWLER_TO"))
  p.add_argument("--max-page", type=int,
                 default=int(os.getenv("CRAWLER_MAX_PAGE", "30")))
  p.add_argument("--size", type=int,
                 default=int(os.getenv("CRAWLER_SIZE", "30")))
  p.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "INFO"),
                 choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
  return p


def make_service() -> CrawlerService:
  logging.info("Create CrawlerService")
  url = os.getenv("DATABASE_URL")
  if not url:
    raise ValueError(
        "DATABASE_URL not set.")

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
  configure_logging(ns.log_level)
  try:
    req = CrawlerRequest.from_cli(ns)
  except ValueError as e:
    logging.error(f"error: {e}")
    sys.exit(2)

  svc = make_service()

  info_parts = [
    f"target={req.provider}",
    f"from={req.from_dt}",
    f"to={req.to_dt}",
    f"max_page={req.max_page}",
    f"size={req.size}",
  ]
  if req.extra:
    info_parts.append(f"extra={req.extra}")
  logging.info("[CRAWLER] Start crawling | " + " | ".join(info_parts))

  svc.execute(request=req)


if __name__ == "__main__":
  main()
