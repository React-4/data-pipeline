from data_collectors.currentPrice import fetch_sector_data
from connector import redis_connector, mysql_connector
from data_collectors import hantwo_api_topN
from data_collectors.disclosure_chatgpt_api import process_disclosures,process_disclosures2
from data_collectors.disclosure_dart_api import fetch_dart_filings
from data_collectors.price_crawler import stock_price_crawler
from data_collectors.stockInfo import stock_info_crawler
import pandas as pd

# MySQL 연결 객체
mc = mysql_connector

# 1. 종목 정보 크롤링 및 저장
# print("종목 정보 크롤링 및 저장 시작...")
# stock_info_df = stock_info_crawler()
# mc.upload_dataframe_to_mysql(stock_info_df, "stock", "append")
#
# # 2. 주가 데이터 크롤링 및 저장
print("주가 데이터 크롤링 및 저장 시작...")
stockInfo_df = mc.read_table_to_dataframe("stock")
days_price_df,weeks_price_df,months_price_df = stock_price_crawler(stockInfo_df,500)

# MySQL에 업로드
mc.upload_dataframe_to_mysql(days_price_df.drop(columns=['ticker']), "stock_price_day", "append")
mc.upload_dataframe_to_mysql(weeks_price_df.drop(columns=['ticker']), "stock_price_week", "append")
mc.upload_dataframe_to_mysql(months_price_df.drop(columns=['ticker']), "stock_price_month", "append")
print("주가 데이터 저장 완료.")

# 3. DART 공시 데이터 수집 및 저장
print("DART 공시 데이터 수집 및 저장 시작...")
# dart_df = fetch_dart_filings('20241124', '20241125', corp_cls='Y', page_count=25)

# 공시 데이터 처리
# chatgpt_api = process_disclosures2(dart_df, stockInfo_df)

# MySQL에 공시 데이터 업로드
# mc.upload_dataframe_to_mysql(chatgpt_api, "announcement", "append")
print("DART 공시 데이터 저장 완료.")

# #4. 실시간 순위 데이터 수집 및 Redis 저장
# print("실시간 순위 데이터 수집 및 Redis 저장 시작...")
# ht = hantwo_api_topN
# redis_client = redis_connector.get_redis_client()
#
# # 상승률, 하락률, 거래량, 거래대금 순위 데이터 수집
# df_up = ht.fetch_change_rate(2)  # 상승률
# df_down = ht.fetch_change_rate(3)  # 하락률
# df_volume = ht.fetch_volume_or_transaction_rank("volume")  # 거래량 순위
# df_transaction = ht.fetch_volume_or_transaction_rank("transaction")  # 거래대금 순위
#
# # Redis에 저장
# redis_connector.save_df_to_redis_as_nested_json(redis_client, df_up, "상승률순위")
# redis_connector.save_df_to_redis_as_nested_json(redis_client, df_down, "하락률순위")
# redis_connector.save_df_to_redis_as_nested_json(redis_client, df_volume, "거래량순위")
# redis_connector.save_df_to_redis_as_nested_json(redis_client, df_transaction, "거래대금순위")
# print("실시간 순위 데이터 저장 완료.")
# exit()
# # 5. KOSPI/KOSDAQ 현재가 데이터 수집 및 Redis 저장
# print("KOSPI/KOSDAQ 현재가 데이터 수집 및 Redis 저장 시작...")
# kospi_current_price = fetch_sector_data('KOSPI')
# kosdaq_current_price = fetch_sector_data('KOSDAQ')
#
# # Redis에 저장
# redis_connector.save_stocks_to_redis(redis_client, kospi_current_price)
# redis_connector.save_stocks_to_redis(redis_client, kosdaq_current_price)
# print("KOSPI/KOSDAQ 현재가 데이터 저장 완료.")
#
# print("모든 작업 완료!")
