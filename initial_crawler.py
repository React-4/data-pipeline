import pandas as pd
import mysql_connector
from stockInfo import stock_info_crawler
from price_crawler import stock_price_crawler
mc = mysql_connector

# 종목 정보 크롤링후 data/listed_companies_with_info.csv 저장
stock_info_crawler()

stock_info_df = pd.read_csv(
    "data/listed_companies_with_info.csv",
    dtype={"ticker": str},  # ticker 컬럼을 str로 읽음 005390이 5390으로 읽히는 문제
    encoding="utf-8-sig"
)

# Stock 테이블 저장
mc.upload_dataframe_to_mysql(stock_info_df,"Stock","append")

# 일봉,주봉,웗봉 주가 크롤링 days_data.csv, weeks_data.csv,  months_data.csv 저장
stock_price_crawler(stock_info_df)

days_price_df = pd.read_csv(
    "data/days_data.csv",
    encoding="utf-8-sig"
)
weeks_price_df = pd.read_csv(
    "data/weeks_data.csv",
    encoding="utf-8-sig"
)
months_price_df = pd.read_csv(
    "data/months_data.csv",
    encoding="utf-8-sig"
)

mc.upload_dataframe_to_mysql(days_price_df,"StockPriceDay","append")

mc.upload_dataframe_to_mysql(weeks_price_df,"StockPriceWeek","append")

mc.upload_dataframe_to_mysql(months_price_df,"StockPriceMonth","append")



# mysql table: Announcement (최대한 api 요청)

# redis: 상승률, 하락률, 거래량, 거래대금 top 30 (0.5초 간격으로)

# redis: 현재 실시간 모든 종목 현재가, 등락율, 등락금액 - 건욱 ()