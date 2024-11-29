from data_collectors.currentPrice import fetch_sector_data
from connector import redis_connector, mysql_connector
from data_collectors import hantwo_api_topN
from data_collectors.disclosure_chatgpt_api import process_disclosures, process_disclosures2
from data_collectors.disclosure_dart_api import fetch_dart_filings
from data_collectors.price_crawler import stock_price_crawler
import pandas as pd
from datetime import datetime
import schedule
import time

# MySQL 및 Redis 연결 객체
mc = mysql_connector
redis_client = redis_connector.get_redis_client()

def get_mysql_connection():
    """
    MySQL 연결 확인 및 재연결 함수.
    """
    global mc
    try:
        # MySQL 연결 상태 확인
        mc.ping(reconnect=True)
    except Exception as e:
        print(f"MySQL 연결 재설정 중...: {e}")
        mc = mysql_connector  # 재연결 수행
    return mc


def get_redis_connection():
    """
    Redis 연결 확인 및 재연결 함수.
    """
    global redis_client
    try:
        # Redis 연결 상태 확인
        redis_client.ping()
    except Exception as e:
        print(f"Redis 연결 재설정 중...: {e}")
        redis_client = redis_connector.get_redis_client()  # 재연결 수행
    return redis_client


# 월~금 하루에 한번 오후 6시 실행
def update_day():
    mc = get_mysql_connection()
    stockInfo_df = mc.read_table_to_dataframe("stock")
    days_price_df = stock_price_crawler(stockInfo_df, "days", 1)
    mc.upload_dataframe_to_mysql(days_price_df, "stock_price_day", "append")


# 매주 금요일 6시에 한번 실행
def update_weeks():
    mc = get_mysql_connection()
    stockInfo_df = mc.read_table_to_dataframe("stock")
    weeks_price_df = stock_price_crawler(stockInfo_df, "weeks", 1)
    mc.upload_dataframe_to_mysql(weeks_price_df, "stock_price_week", "append")


# 매달 1일 한번 실행
def update_months():
    if datetime.now().day != 1:
        return

    mc = get_mysql_connection()
    stockInfo_df = mc.read_table_to_dataframe("stock")
    months_price_df = stock_price_crawler(stockInfo_df, "months", 1)
    mc.upload_dataframe_to_mysql(months_price_df, "stock_price_month", "append")


# 매일 10분에 한번씩 공시 크롤링
previous_row_count = 0


def reset_previous_row_count():
    global previous_row_count
    previous_row_count = 0
    print(f"{datetime.now()} - previous_row_count 초기화 완료.")


def update_10m():
    global previous_row_count
    mc = get_mysql_connection()
    stockInfo_df = mc.read_table_to_dataframe("stock")
    today = datetime.today().strftime('%Y%m%d')
    dart_df = fetch_dart_filings(today, today, corp_cls='Y', page_count=25)
    current_row_count = len(dart_df)

    if current_row_count > previous_row_count:
        new_rows = dart_df.iloc[previous_row_count:]
        # print(f"New rows detected: {len(new_rows)}")
        previous_row_count = current_row_count
        df = process_disclosures2(new_rows, stockInfo_df)
        mc.upload_dataframe_to_mysql(df, "announcement", "append")
    else:
        print("No new rows detected.")


# 매 1분마다 실행
def update_1m():
    redis_client = get_redis_connection()
    print("실시간 순위 데이터 수집 및 Redis 저장 시작...")
    ht = hantwo_api_topN

    # 상승률, 하락률, 거래량, 거래대금 순위 데이터 수집
    df_up = ht.fetch_change_rate(2)
    time.sleep(1)
    df_down = ht.fetch_change_rate(3)
    time.sleep(1)
    df_volume = ht.fetch_volume_or_transaction_rank("volume")
    time.sleep(1)
    df_transaction = ht.fetch_volume_or_transaction_rank("transaction")
    time.sleep(1)

    # Redis에 저장
    redis_connector.save_df_to_redis_as_nested_json(redis_client, df_up, "상승률순위")
    redis_connector.save_df_to_redis_as_nested_json(redis_client, df_down, "하락률순위")
    redis_connector.save_df_to_redis_as_nested_json(redis_client, df_volume, "거래량순위")
    redis_connector.save_df_to_redis_as_nested_json(redis_client, df_transaction, "거래대금순위")

    # 5. KOSPI/KOSDAQ 현재가 데이터 수집 및 Redis 저장
    print("KOSPI/KOSDAQ 현재가 데이터 수집 및 Redis 저장 시작...")
    kospi_current_price = fetch_sector_data('KOSPI')
    kosdaq_current_price = fetch_sector_data('KOSDAQ')

    # Redis에 저장
    redis_connector.save_stocks_to_redis(redis_client, kospi_current_price)
    redis_connector.save_stocks_to_redis(redis_client, kosdaq_current_price)
    print("KOSPI/KOSDAQ 현재가 데이터 저장 완료.")

    print("실시간 순위 데이터 저장 완료.")


# 작업 스케줄링
def main():
    schedule.every().monday.at("18:00").do(update_day)
    schedule.every().tuesday.at("18:00").do(update_day)
    schedule.every().wednesday.at("18:00").do(update_day)
    schedule.every().thursday.at("18:00").do(update_day)
    schedule.every().friday.at("18:00").do(update_day)
    schedule.every().day.at("00:00").do(reset_previous_row_count)
    schedule.every().friday.at("18:00").do(update_weeks)
    schedule.every().friday.at("18:30").do(update_months)
    schedule.every(10).minutes.do(update_10m)
    schedule.every(1).minutes.do(update_1m)

    print("스케줄링 시작...")
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
    # update_weeks()
    # update_months()
    # update_10m()
    # update_1m()