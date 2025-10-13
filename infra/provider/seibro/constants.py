# infra/provider/seibro/constants.py

# ====== 통신(Endpoint) 상수 ======
CONTROL_URL = "https://seibro.or.kr/websquare/control.jsp"
CALL_URL = "https://seibro.or.kr/websquare/engine/proworks/callServletService.jsp"
ROOT_URL = "https://seibro.or.kr/"

# ====== 헤더/포맷 상수 ======
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)
ACCEPT = "application/xml"
ACCEPT_LANGUAGE = "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
X_REQUESTED_WITH = "XMLHttpRequest"
ORIGIN = "https://seibro.or.kr"
CONTENT_TYPE = "application/xml; charset=UTF-8"

DEFAULT_HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": ACCEPT,
    "Accept-Language": ACCEPT_LANGUAGE,
    "X-Requested-With": X_REQUESTED_WITH,
    "Origin": ORIGIN,
    "Content-Type": CONTENT_TYPE,
}

SUBMISSION_PREFIX = "submission_"
DATE_FMT = "%Y%m%d"

# ====== XML/Param 키 상수 ======
K_MENU_NO = "MENU_NO"
K_CMM_BTN_ABBR_NM = "CMM_BTN_ABBR_NM"
K_W2XPATH = "W2XPATH"
K_START_PAGE = "START_PAGE"
K_END_PAGE = "END_PAGE"
K_FROM_DT = "fromRGT_STD_DT"
K_TO_DT = "toRGT_STD_DT"

# 도메인별 파라미터 키
K_ETF_SORT_LEVEL_CD = "etf_sort_level_cd"
K_ETF_BIG_SORT_CD = "etf_big_sort_cd"
K_ETF_SORT_CD = "etf_sort_cd"
K_ISIN = "isin"
K_MNGCO_CUSTNO = "mngco_custno"
K_RGT_RSN_DTAIL_SORT_CD = "RGT_RSN_DTAIL_SORT_CD"

# ====== 기본값 상수 (SeibroRequest 용) ======
DEFAULT_ACTION = "exerInfoDtramtPayStatPlist"
DEFAULT_TASK = "ksd.safe.bip.cnts.etf.process.EtfExerInfoPTask"
DEFAULT_W2XPATH = "/IPORTAL/user/etf/BIP_CNTS06030V.xml"
DEFAULT_MENU_NO = "179"
DEFAULT_CMM_BTN_ABBR_NM = (
    "total_search,openall,print,hwp,word,pdf,searchIcon,searchIcon,"
    "seach,searchIcon,seach,"
)
DEFAULT_START_PAGE = "1"
DEFAULT_END_PAGE = "1"

DEFAULT_ETF_SORT_LEVEL_CD = "0"
DEFAULT_ETF_BIG_SORT_CD = ""
DEFAULT_ETF_SORT_CD = ""
DEFAULT_ISIN = ""
DEFAULT_MNGCO_CUSTNO = ""
DEFAULT_RGT_RSN_DTAIL_SORT_CD = ""

PROVIDER_SEIBRO = "seibro"

SEIBRO_FIELD_MAPPING = {
    "isin": ["ISIN"],
    "pay_base_date": ["RGT_STD_DT"],
    "actual_pay_date": ["TH1_PAY_TERM_BEGIN_DT"],
    "div_type": ["RGT_RSN_DTAIL_NM"],
    "dist_per_share": ["BUNBE"],
    "tax_std": ["TAX_STD"],
    "estm_stdprc": ["ESTM_STDPRC"],
}
