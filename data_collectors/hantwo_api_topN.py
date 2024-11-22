import requests
import pandas as pd

from data_collectors import hantwo_api_token

APP_KEY = hantwo_api_token.APP_KEY
APP_SECRET = hantwo_api_token.APP_SECRET
token = hantwo_api_token.get_access_token()

BASE_URL = "https://openapi.koreainvestment.com:9443"

# 공통 헤더
headers = {
    "Content-Type": "application/json; charset=utf-8",
    "authorization": f"Bearer {token}",
    "appkey": APP_KEY,
    "appsecret": APP_SECRET
}

# 상승률/하락률 요청
def fetch_change_rate(num=2):
    local_headers = headers.copy()
    local_headers["tr_id"] = "FHPST01700000"

    params = {
        "fid_rsfl_rate2": "",
        "fid_cond_mrkt_div_code": "J",
        "fid_cond_scr_div_code": "20170",
        "fid_input_iscd": "0000",
        "fid_rank_sort_cls_code": num,  # 2: 상승률, 3: 하락률
        "fid_input_cnt_1": 0,
        "fid_prc_cls_code": "0",
        "fid_input_price_1": "",
        "fid_input_price_2": "",
        "fid_vol_cnt": "",
        "fid_trgt_cls_code": "0",
        "fid_trgt_exls_cls_code": "0",
        "fid_div_cls_code": "0",
        "fid_rsfl_rate1": ""
    }

    description = "상승률 순위" if num == 2 else "하락률 순위"
    response = requests.get(f"{BASE_URL}/uapi/domestic-stock/v1/ranking/fluctuation", headers=local_headers, params=params)
    return parse_response_to_df(response, description)


# 거래량/거래대금 요청
def fetch_volume_or_transaction_rank(rank_type="volume"):
    local_headers = headers.copy()
    local_headers["tr_id"] = "FHPST01710000"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_COND_SCR_DIV_CODE": "20171",
        "FID_INPUT_ISCD": "0000",
        "FID_DIV_CLS_CODE": "0",
        "FID_TRGT_CLS_CODE": "111111111",
        "FID_TRGT_EXLS_CLS_CODE": "0000000000",
        "FID_INPUT_PRICE_1": "",
        "FID_INPUT_PRICE_2": "",
        "FID_VOL_CNT": "",
        "FID_INPUT_DATE_1": ""
    }

    if rank_type == "volume":
        params["FID_BLNG_CLS_CODE"] = "0"  # 평균 거래량 기준
        description = "거래량 순위"
    elif rank_type == "transaction":
        params["FID_BLNG_CLS_CODE"] = "3"  # 거래대금 기준
        description = "거래대금 순위"
    else:
        raise ValueError("Invalid rank_type. Use 'volume' or 'transaction'.")

    response = requests.get(f"{BASE_URL}/uapi/domestic-stock/v1/quotations/volume-rank", headers=local_headers, params=params)
    return parse_response_to_df(response, description)


# 응답 처리 함수 (DataFrame으로 변환)
def parse_response_to_df(response, description):
    print(f"==== {description} ====")
    print(f"Response Status: {response.status_code}")
    response_data = response.json()

    if response.status_code == 200 and response_data.get("rt_cd") == "0":
        output = response_data.get("output", [])
        if output:
            data = []
            for item in output:
                # 공통 필드를 데이터 리스트에 추가
                row = {
                    "종목명": item.get("hts_kor_isnm"),
                    "종목코드": item.get("stck_shrn_iscd") or item.get("mksc_shrn_iscd"),
                    "현재가": item.get("stck_prpr"),
                    "등락률": item.get("oprc_vrss_prpr_rate") if description in ["상승률 순위", "하락률 순위"] else item.get("prdy_ctrt"),
                    "거래량": item.get("acml_vol")
                }
                data.append(row)
            # DataFrame 생성
            df = pd.DataFrame(data)
            print(df)
            return df
        else:
            print(f"{description} 데이터를 가져오지 못했습니다.")
            return pd.DataFrame()
    else:
        print(f"API 요청에 실패했습니다. Response: {response_data}")
        return pd.DataFrame()


# # 실행
# df_up = fetch_change_rate(2)  # 상승률
# df_down = fetch_change_rate(3)  # 하락률
# df_volume = fetch_volume_or_transaction_rank("volume")  # 거래량 순위
# df_transaction = fetch_volume_or_transaction_rank("transaction")  # 거래대금 순위
#
# # CSV로 저장
# df_up.to_csv("data/상승률순위.csv", index=False, encoding="utf-8-sig")
# df_down.to_csv("data/하락률순위.csv", index=False, encoding="utf-8-sig")
# df_volume.to_csv("data/거래량순위.csv", index=False, encoding="utf-8-sig")
# df_transaction.to_csv("data/거래대금순위.csv", index=False, encoding="utf-8-sig")
