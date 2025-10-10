import unittest

from domain.extractor_interface import RawResponse
from infra.extractor.xml_extractor import XmlExtractor

SAMPLE_DATA="""
<vector beforeServletCall="1758972022689" beforeEJBCall="1758972022696" afterServletCall="1758972023121" afterEJBCall="1758972023119" result="30">
    <data vectorkey="0" type="Document">
        <result><ISIN value="KR7276970001"/><KOR_SECN_NM value="KODEX 미국S&amp;P500배당귀족커버드콜(합성 H)"/><ETF_SORT_CD value="P0301"/><ISSUCO_CUSTNO value="216516"/><RGT_STD_DT value="20250924"/><TH1_PAY_TERM_BEGIN_DT value="20250926"/><ESTM_STDPRC value="116"/><BUNBE value="1.52833"/><ETF_SORT_NM value="파생상품/구조화"/><REP_SECN_NM value="삼성자산운용"/><TAXSTD value="9504.15"/><RGT_RSN_DTAIL_NM value="이익분배"/></result>
    </data>
    <data vectorkey="1" type="Document">
        <result><ISIN value="KR7407170000"/><KOR_SECN_NM value="KCGI 스마트커머스액티브"/><ETF_SORT_CD value="M0901"/><ISSUCO_CUSTNO value="248998"/><RGT_STD_DT value="20250921"/><TH1_PAY_TERM_BEGIN_DT value="20250922"/><ESTM_STDPRC value="9944.968864"/><BUNBE value=""/><ETF_SORT_NM value="테마/기타"/><REP_SECN_NM value="케이씨지아이자산운용"/><TAXSTD value="10626.34728"/><RGT_RSN_DTAIL_NM value="청산분배"/></result>
    </data>
    <data vectorkey="2" type="Document">
        <result><ISIN value="KR7433870003"/><KOR_SECN_NM value="PLUS TDF2050액티브"/><ETF_SORT_CD value="Z0101"/><ISSUCO_CUSTNO value="251791"/><RGT_STD_DT value="20250921"/><TH1_PAY_TERM_BEGIN_DT value="20250922"/><ESTM_STDPRC value="15312.67447142857142"/><BUNBE value=""/><ETF_SORT_NM value="기타/기타"/><REP_SECN_NM value="한화자산운용"/><TAXSTD value="15274.21840476190476"/><RGT_RSN_DTAIL_NM value="청산분배"/></result>
    </data>
</vector>
"""

class TestExtractor(unittest.TestCase):
  def test_extract(self):
    xml = XmlExtractor()
    resp = RawResponse(text=SAMPLE_DATA)
    result = list(xml.parse(resp))

    # 기본 구조 검증
    self.assertEqual(len(result), 3)

    # 첫 번째 결과 검증
    first = result[0]
    self.assertEqual(first["ISIN"], "KR7276970001")
    self.assertEqual(first["RGT_STD_DT"], "20250924")
    self.assertEqual(first["TH1_PAY_TERM_BEGIN_DT"], "20250926")
    self.assertEqual(first["BUNBE"], "1.52833")
    self.assertEqual(first["RGT_RSN_DTAIL_NM"], "이익분배")

    # 두 번째 결과 검증
    second = result[1]
    self.assertEqual(second["ISIN"], "KR7407170000")
    self.assertEqual(second["RGT_RSN_DTAIL_NM"], "청산분배")

    # 세 번째 결과 검증
    third = result[2]
    self.assertEqual(third["ISIN"], "KR7433870003")
    self.assertEqual(third["ETF_SORT_CD"], "Z0101")

if __name__ == "__main__":
  unittest.main()