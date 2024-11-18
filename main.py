import pandas as pd
import price_crawler

df = pd.read_csv("data/listed_companies.csv", dtype={'종목코드': str})
df = df[["회사명","종목코드"]].reset_index().rename(columns={"index": "stock_id"})

pc = price_crawler.stock_price_crawler(df)
