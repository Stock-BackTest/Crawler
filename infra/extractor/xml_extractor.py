import xml.etree.ElementTree as ET
from typing import List, Iterable, Dict

from domain.extractor_interface import DividendExtractor, RawResponse


class XmlDividendExtractor(DividendExtractor):
  def __init__(self, row_tags: List[str] | None = None):
    self.row_tags = row_tags or ["result"]

  def can_handle(self, raw: RawResponse) -> bool:
    if raw.mime and "xml" in raw.mime.lower():
      return True
    t = raw.text.lstrip()
    return t.startswith("<?xml") or "<vector" in t or "<result" in t

  def parse(self, raw: RawResponse) -> Iterable[dict]:
    try:
      root = ET.fromstring(raw.text)
    except ET.ParseError:
      return []

    rows: List[Dict[str, str]] = []

    for tag in self.row_tags:
      for node in root.findall(f".//{tag}"):
        record: Dict[str, str] = {}
        for child in list(node):
          key = child.tag
          if not key:
            continue
          val = child.attrib.get("value", (
                child.text or "").strip() if child.text else "")
          record[key] = val
        if any(record.values()):
          rows.append(record)

    return rows
