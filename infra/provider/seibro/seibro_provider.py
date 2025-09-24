import random
import requests
import time

from domain.provider_interface import ProviderInterface
from infra.provider.seibro.requests.seibro_request import SeibroRequest

CONTROL_URL = "https://seibro.or.kr/websquare/control.jsp"
CALL_URL = "https://seibro.or.kr/websquare/engine/proworks/callServletService.jsp"


class SeibroProvider(ProviderInterface):
  def __init__(self, timeout: int = 20, max_retries: int = 3):
    self.s = requests.Session()
    self.s.headers.update({
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
      "Accept": "application/xml",
      "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
      "X-Requested-With": "XMLHttpRequest",
      "Origin": "https://seibro.or.kr",
      "Content-Type": "application/xml; charset=UTF-8",
    })
    self.timeout = timeout
    self.max_retries = max_retries

  def _prime(self, w2xpath: str, menu_no: str):
    try:
      self.s.get("https://seibro.or.kr/", timeout=self.timeout)
    except:
      pass
    ref = f"{CONTROL_URL}?w2xPath={w2xpath}&menuNo={menu_no}"
    self.s.get(ref, timeout=self.timeout)
    self.s.headers["Referer"] = ref


  def fetch(self, req: SeibroRequest):
    self._prime(req.w2xpath, req.menu_no)

    self.s.headers["submissionid"] = f"submission_{req.action}"

    payload = req.to_xml()

    last_err = None
    for attempt in range(1, self.max_retries + 1):
      try:
        r = self.s.post(CALL_URL, data=payload, timeout=self.timeout)
        text = r.text
        if "<WARNING" in text:
          raise RuntimeError(f"Server WARNING: {text[:240]}")
        r.raise_for_status()
        return text
      except Exception as e:
        last_err = e
        time.sleep((1.2 ** attempt) + random.random())
    raise RuntimeError(f"POST failed: {last_err}")
