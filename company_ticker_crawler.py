import pandas as pd
import requests

# URL of the page
url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

try:
    # Fetch the page content
    response = requests.get(url)
    response.encoding = "euc-kr"  # KRX 사이트는 EUC-KR 인코딩을 사용하는 경우가 많음
    # Parse HTML tables
    tables = pd.read_html(response.text)
    # Assuming the first table is the desired one
    listed_companies_df = tables[0]

    # Convert '종목코드' column to string and pad with leading zeros to maintain length
    if "종목코드" in listed_companies_df.columns:
        listed_companies_df["종목코드"] = listed_companies_df["종목코드"].astype(str).str.zfill(6)

    # Display the first few rows of the DataFrame to verify
    print(listed_companies_df.head())

    # Save to a CSV file
    listed_companies_df.to_csv("data/listed_companies.csv", index=False, encoding="utf-8-sig")
    print("CSV 파일로 저장되었습니다: listed_companies.csv")
except Exception as e:
    print(f"오류 발생: {e}")
