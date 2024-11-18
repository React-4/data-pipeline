from connector import Connector
from enum import IntEnum, Enum
import requests
from logger import logger


class DateScale(IntEnum):
    DAY = 0
    WEEK = 1
    MONTH = 2


class DomesticMarket(Connector):
    class MarketCode(Enum):
        ALL = "0000"
        KOSPI = "0001"
        KOSPI200 = "2001"
        KOSDAQ = "1001"

    def __init__(self):
        super().__init__()

    def get_stock_ranking(self, market_code=MarketCode):
        url = f"{Connector.base_url}/uapi/domestic-stock/v1/ranking/fluctuation"
        headers = self.form_common_headers(tr_id="FHPST01700000", custtype="P")
        payload = {
            "fid_rsfl_rate2": ""  # 등락 비율2	String	Y	132	입력값 없을때 전체 (~ 비율
            , "fid_cond_mrkt_div_code": "J"  # 조건 시장 분류 코드	String	Y	2	시장구분코드 (주식 J)
            , "fid_cond_scr_div_code": "20170"  # 조건 화면 분류 코드	String	Y	5	Unique key( 20170 )
            , "fid_input_iscd": "0000"  # 입력 종목코드	String	Y	12	0000(전체) 코스피(0001), 코스닥(1001), 코스피200(2001)
            , "fid_rank_sort_cls_code": "0"  # 순위 정렬 구분 코드	String	Y	2	0:상승율순 1:하락율순 2:시가대비상승율 3:시가대비하락율 4:변동율
            , "fid_input_cnt_1": "0"  # 입력 수1	String	Y	12	0:전체 , 누적일수 입력
            , "fid_prc_cls_code": "1"  # 가격 구분 코드	String	Y	2	'fid_rank_sort_cls_code :0 상승율 순일때 (0:저가대비, 1:종가대비
            , "fid_input_price_1": ""  # 입력 가격1	String	Y	12	입력값 없을때 전체 (가격 ~)
            , "fid_input_price_2": ""  # 입력 가격2	String	Y	12	입력값 없을때 전체 (~ 가격)
            , "fid_vol_cnt": ""  # 거래량 수	String	Y	12	입력값 없을때 전체 (거래량 ~)
            , "fid_trgt_cls_code": "0"  # 대상 구분 코드	String	Y	32	0:전체
            , "fid_trgt_exls_cls_code": "0"  # 대상 제외 구분 코드	String	Y	32	0:전체
            , "fid_div_cls_code": "0"  # 분류 구분 코드	String	Y	2	0:전체
            , "fid_rsfl_rate1": ""  # 등락 비율1	String	Y	132	입력값 없을때 전체 (비율 ~)
        }
        logger.info(f"payload : {payload}")
        response = requests.get(
            url=url,
            headers=headers,
            params=payload
        )

        return response.json()

    def get_volumne_ranking(self):
        url = f"{Connector.base_url}/uapi/domestic-stock/v1/quotations/volume-rank"
        headers = self.form_common_headers(tr_id="FHPST01710000", custtype="P")
        payload = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_COND_SCR_DIV_CODE": "20171",
            "FID_INPUT_ISCD": "0000",
            "FID_DIV_CLS_CODE": "0",
            "FID_BLNG_CLS_CODE": "2",  # 0 : 평균거래량 s1:거래증가율 2:평균거래회전율 3:거래금액순 4:평균거래금액회전율
            "FID_TRGT_CLS_CODE": "111111111",
            "FID_TRGT_EXLS_CLS_CODE": "0000000000",
            "FID_INPUT_PRICE_1": "",
            "FID_INPUT_PRICE_2": "",
            "FID_VOL_CNT": "",
            "FID_INPUT_DATE_1": ""
        }

        logger.info(f"payload : {payload}")
        response = requests.get(
            url=url,
            headers=headers,
            params=payload
        )
        return response.json()


class ForeignMarket(Connector):

    def __init__(self):
        super().__init__()

    def get_historical_price(self, exchanger_code, ticker, scale, start_from):
        url = f"{Connector.base_url}/uapi/overseas-price/v1/quotations/dailyprice"
        headers = self.form_common_headers(tr_id="HHDFS76240000", custtype="P")
        payload = {
            "AUTH": "",
            "EXCD": exchanger_code,
            "SYMB": ticker,
            "GUBN": str(scale),
            "BYMD": start_from,
            "MODP": "0"
        }
        logger.info(payload)
        response = requests.get(
            url=url,
            headers=headers,
            params=payload
        )

        return response.json()


if __name__ == "__main__":
    # this is test
    engine = ForeignMarket()
    ret = engine.get_historical_price("NAS", "TSLA", DateScale.MONTH, "20240724")
    print(ret)