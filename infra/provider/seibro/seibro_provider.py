import random
import time

import requests

from domain.provider_interface import DividendProvider
from infra.provider.seibro import constants as C
from infra.provider.seibro.requests.seibro_request import SeibroRequest


class SeibroDividendProvider(DividendProvider):
  request_type: ClassVar[Type[SeibroRequest]] = SeibroRequest

  def __init__(self, timeout: int = 20, max_retries: int = 3):
    self.s = requests.Session()
    self.s.headers.update(C.DEFAULT_HEADERS)
    self.timeout = timeout
    self.max_retries = max_retries

  def _prime(self, w2xpath: str, menu_no: str):
    try:
      self.s.get(C.ROOT_URL, timeout=self.timeout)
    except Exception:
      pass

    ref = f"{C.CONTROL_URL}?w2xPath={w2xpath}&menuNo={menu_no}"
    self.s.get(ref, timeout=self.timeout)
    self.s.headers["Referer"] = ref

  def fetch(self, req: SeibroRequest):
    self._prime(req.w2xpath, req.menu_no)

    self.s.headers["submissionid"] = f"{C.SUBMISSION_PREFIX}{req.action}"

    payload = req.to_xml()

    last_err = None
    for attempt in range(1, self.max_retries + 1):
      try:
        r = self.s.post(C.CALL_URL, data=payload, timeout=self.timeout)
        text = r.text
        if "<WARNING" in text:
          raise RuntimeError(f"Server WARNING: {text[:240]}")
        r.raise_for_status()
        return text
      except Exception as e:
        last_err = e
        time.sleep((1.2 ** attempt) + random.random())
    raise RuntimeError(f"POST failed: {last_err}")
