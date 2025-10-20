import logging
import random
import threading
import time
from typing import ClassVar, Type

import requests

from domain.provider_interface import DividendProvider, BaseProviderRequest
from infra.provider.seibro import constants as C
from infra.provider.seibro.requests.seibro_request import SeibroRequest


class SeibroDividendProvider(DividendProvider):
  request_type: ClassVar[Type[SeibroRequest]] = SeibroRequest

  _SESSION: ClassVar[requests.Session | None] = None
  _LOCK: ClassVar[threading.Lock] = threading.Lock()

  @classmethod
  def _get_session(cls) -> requests.Session:
    if cls._SESSION is None:
      with cls._LOCK:
        if cls._SESSION is None:
          s = requests.Session()
          s.headers.update(C.DEFAULT_HEADERS)
          cls._SESSION = s
    return cls._SESSION

  def __init__(self, timeout: int = 20, max_retries: int = 3):
    self.s = requests.Session()
    self.s.headers.update(C.DEFAULT_HEADERS)
    self.timeout = timeout
    self.max_retries = max_retries

  def _prime(self, w2xpath: str, menu_no: str) -> str:
    try:
      self.s.get(C.ROOT_URL, timeout=self.timeout)
    except Exception:
      pass

    ref = f"{C.CONTROL_URL}?w2xPath={w2xpath}&menuNo={menu_no}"
    self.s.get(ref, timeout=self.timeout)
    logging.debug(f"[PROVIDER] {self.s.headers}")
    return ref

  def fetch(self, req: SeibroRequest) -> requests.Response:
    logging.info(f"[PROVIDER] session url: {C.ROOT_URL}")

    self.s.headers["Referer"] = self._prime(req.w2xpath, req.menu_no)
    self.s.headers["submissionid"] = f"{C.SUBMISSION_PREFIX}{req.action}"

    payload = req.to_xml()
    logging.debug(f"[PROVIDER] payload: {payload}")

    last_err = None
    for attempt in range(1, self.max_retries + 1):
      try:
        r = self.s.post(C.CALL_URL, data=payload, timeout=self.timeout)
        text = r.text
        if "<WARNING" in text:
          raise RuntimeError(f"Server WARNING: {text[:240]}")
        r.raise_for_status()
        logging.debug(
          f"[PROVIDER] response - \nstatus: {r.status_code}\nbody: {r.text}")
        return r
      except Exception as e:
        last_err = e
        time.sleep((1.2 ** attempt) + random.random())
    raise RuntimeError(f"POST failed: {last_err}")

  def supports(self, req: BaseProviderRequest) -> bool:
    return isinstance(req, self.request_type)
