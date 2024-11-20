import pandas as pd
import price_crawler
import currentPrice

df = pd.read_csv("data/listed_companies.csv", dtype={'종목코드': str})
df = df[["회사명","종목코드"]].reset_index().rename(columns={"index": "stock_id"})

pc = price_crawler.stock_price_crawler(df)
cp = currentPrice()


# mysql table: Stock (하루에 한번)

# mysql table: StockPriceDay, StockPriceWeek,StockPriceMonth (하루에 한번 장종료 후)

# mysql table: Announcement (최대한 api 요청)

# redis: 상승률, 하락률, 거래량, 거래대금 top 30 (0.5초 간격으로)

# redis: 현재 실시간 모든 종목 현재가, 등락율, 등락금액 - 건욱 ()
