import datetime as dt
import unittest
from unittest.mock import patch
import requests

from infra.provider.seibro.requests.seibro_request import SeibroRequest
from infra.provider.seibro.seibro_provider import SeibroDividendProvider
from tests.common.fixtures.request_fixtures import make_seibro_req, OtherRequest

SAMPLE_VECTOR = """<?xml version="1.0" encoding="UTF-8" ?>
<vector beforeServletCall="1" beforeEJBCall="1" afterServletCall="1" result="2">
  <data vectorkey="0" type="Document"><result><ISIN value="KR123"/></result></data>
  <data vectorkey="1" type="Document"><result><ISIN value="KR456"/></result></data>
</vector>
"""


def _response_of(body: str, status: int = 200, headers: dict | None = None,
                 url: str = "https://example.com") -> requests.Response:
    r = requests.Response()
    r.status_code = status
    r._content = body.encode("utf-8")
    r.encoding = "utf-8"
    r.url = url
    if headers:
        r.headers.update(headers)
    return r


class TestSeibroProvider(unittest.TestCase):
  def test_fetch_mock(self):
    provider = SeibroDividendProvider(timeout=5, max_retries=1)

    with patch("infra.provider.seibro.seibro_provider.requests.Session.get") as mock_get, \
         patch("infra.provider.seibro.seibro_provider.requests.Session.post") as mock_post:

      mock_get.return_value = _response_of("OK")
      mock_post.return_value = _response_of(
          SAMPLE_VECTOR,
          headers={"Content-Type": "application/xml; charset=UTF-8"},
          url="https://seibro.or.kr/websquare/executor/control.jsp",
      )

      req = make_seibro_req(page=(1, 30))

      result = provider.fetch(req)

      self.assertIsInstance(result, requests.Response)
      self.assertIn("<vector", result.text)
      self.assertIn('result="2"', result.text)

      self.assertTrue(mock_get.called)
      mock_post.assert_called_once()

      self.assertEqual(
          provider.s.headers.get("submissionid"),
          "submission_exerInfoDtramtPayStatPlist",
      )
      self.assertIn("control.jsp", provider.s.headers.get("Referer", ""))

  def test_to_xml_minimal_contract(self):
    req = SeibroRequest()
    xml = req.to_xml()
    self.assertIn("<reqParam", xml)
    self.assertIn("<MENU_NO", xml)
    self.assertIn("<CMM_BTN_ABBR_NM", xml)
    self.assertIn("<W2XPATH", xml)
    self.assertLess(xml.index("<MENU_NO"), xml.index("<CMM_BTN_ABBR_NM"))
    self.assertLess(xml.index("<CMM_BTN_ABBR_NM"), xml.index("<W2XPATH"))

  def test_date_defaults_and_swap(self):
    d = SeibroRequest()
    self.assertLessEqual(d.from_dt, d.to_dt)

    a = dt.date(2025, 9, 21)
    b = dt.date(2025, 9, 15)
    d2 = SeibroRequest(from_dt=a, to_dt=b)
    self.assertEqual(d2.from_dt, b)
    self.assertEqual(d2.to_dt, a)

  def test_supports_request_type(self):
    provider = SeibroDividendProvider(timeout=5, max_retries=1)

    self.assertTrue(provider.supports(SeibroRequest()))
    self.assertFalse(provider.supports(OtherRequest()))
    self.assertFalse(provider.supports(object()))


if __name__ == "__main__":
  unittest.main()
