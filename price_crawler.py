import requests
import json
import os
from tqdm import tqdm

def fetch_stock_data(interval, stock_id, ticker, limit=1000):
    """
    Fetch stock data for a specific interval (day, week, month) and return it as a list of dictionaries.
    """
    try:
        # URL 설정
        url = f'https://finance.daum.net/api/charts/A{ticker}/{interval}?limit={limit}&adjusted=true'

        # 헤더 설정
        headers = {
            'referer': f'https://finance.daum.net/quotes/{ticker}',
        }

        # 데이터 요청
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 요청이 실패하면 예외 발생

        # 데이터 파싱
        raw_data = response.json()['data']

        # 데이터 변환
        transformed_data = [
            {
                "stock_id": stock_id,
                "ticker": ticker,
                "date": record["date"],
                "open_price": int(record["openingPrice"]),
                "high_price": int(record["highPrice"]),
                "low_price": int(record["lowPrice"]),
                "close_price": int(record["tradePrice"]),
                "volume": int(record["candleAccTradeVolume"]),
                "change_rate": float(record["changeRate"]) if record["changeRate"] is not None else None
            }
            for record in raw_data
        ]

        return transformed_data
    except requests.exceptions.RequestException as e:
        print(f'데이터를 가져오는 중 오류가 발생했습니다: {e}')
        return []
    except KeyError as e:
        print(f'필수 데이터가 응답에 없습니다: {e}')
        return []

def stock_price_crawler(df):
    """
    Crawl stock prices for multiple stocks and save to unified JSON files (day, week, month).
    """
    # 호출: 일봉, 주봉, 월봉 데이터를 각각 저장
    intervals = ['days', 'weeks', 'months']
    unified_data = {interval: [] for interval in intervals}

    # 각 종목에 대해 크롤링 수행
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing stocks"):
        stock_id = row["stock_id"]
        ticker = row["종목코드"]

        for interval in intervals:
            data = fetch_stock_data(interval, stock_id, ticker, limit=1000)
            unified_data[interval].extend(data)  # 데이터를 통합

    # 통합 데이터를 각각의 파일로 저장
    os.makedirs('data', exist_ok=True)  # 데이터 디렉토리 생성
    for interval in intervals:
        file_name = f'data/{interval}_data.json'
        with open(file_name, 'w', encoding='utf-8') as json_file:
            json.dump(unified_data[interval], json_file, indent=2, ensure_ascii=False)
        print(f'{interval.capitalize()} 데이터가 성공적으로 저장되었습니다: {file_name}')