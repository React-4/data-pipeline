import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from io import StringIO
from tqdm import tqdm

# KRX 페이지 URL
krx_url = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

def parse_market_cap(market_cap_str):
    market_cap_str = market_cap_str.replace(' ', '').replace('\t', '')  # 공백 및 탭 제거
    billions = 0
    trillions = 0

    if '조' in market_cap_str:
        trillions_part = market_cap_str.split('조')[0]
        trillions = int(trillions_part.replace(',', '')) * 10000  # 조를 억원으로 변환

    if '억원' in market_cap_str:
        billions_part = market_cap_str.split('억원')[0].split('조')[-1]
        if billions_part:
            billions = int(billions_part.replace(',', ''))

    total_market_cap = trillions + billions
    return total_market_cap

# Daum 금융에서 추가 기업 정보를 가져오는 함수
def get_daum_company_info(ticker):
    daum_url = f"http://finance.naver.com/item/main.naver?code={ticker}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(daum_url, headers=headers)
    html = response.content.decode('euc-kr','replace')    

    # HTML 파싱
    soup = BeautifulSoup(html, 'html.parser')
    # 필요한 정보 추출
    try:
        # 기업개요
        company_summary_element = soup.select_one('div.summary_info')
        if company_summary_element:
            paragraphs = company_summary_element.find_all('p')
            company_summary_text = ' '.join([p.get_text(strip=True) for p in paragraphs])
        else:
            company_summary_text = "정보 없음"
        
        # 시가총액
        market_cap_element = soup.select_one('tr:has(th:contains("시가총액")) td em')  
        market_cap_value = market_cap_element.text.strip()
        market_cap_unit = "억원"  # 단위
        market_cap_text = f"{market_cap_value} {market_cap_unit}".replace('\n', '').replace('\t', '').replace(' ', '').strip()

        # 시장 타입
        market_type_element = soup.select_one('dl.blind dd:contains("종목코드")')  # 종목코드 정보
        if market_type_element:
            market_type_text = market_type_element.text.strip()
            # "코스피" 또는 "코스닥" 확인
            if "코스피" in market_type_text:
                market_type_text = "KOSPI"
            elif "코스닥" in market_type_text:
                market_type_text = "KOSDAQ"
            else:
                market_type_text = "정보 없음"

        return {
            "기업개요": company_summary_text,
            "시가총액": parse_market_cap(market_cap_text),
            "마켓타입": market_type_text
        }
    except Exception as e:
        print(f"정보 추출 오류: {e}")
        print(f"종목코드: {ticker}")
        return {
            "현재 가격": None,
            "시가총액": None,
            "마켓타입": None
        }

def stock_info_crawler():
    try:
        # KRX 페이지 콘텐츠 가져오기
        response = requests.get(krx_url)
        response.encoding = "euc-kr"

        # HTML 테이블 파싱
        tables = pd.read_html(StringIO(response.text))

        # 첫 번째 테이블을 선택
        listed_companies_df = tables[0]

        # 필요한 열 선택: 종목코드, 회사명, 업종
        listed_companies_df = listed_companies_df[["종목코드", "회사명", "업종"]]

        # '종목코드' 열을 문자열로 변환하고 6자리로 패딩
        if "종목코드" in listed_companies_df.columns:
            listed_companies_df.loc[:, "종목코드"] = listed_companies_df["종목코드"].astype(str).str.zfill(6)

        # 추가 기업 정보 가져오기
        additional_info = []
        for index, row in tqdm(listed_companies_df.iterrows(), total=len(listed_companies_df),
                               desc="Processing companies"):
            ticker = row["종목코드"]
            company_info = get_daum_company_info(ticker)
            additional_info.append(company_info)

        # 추가 정보 DataFrame으로 변환
        additional_info_df = pd.DataFrame(additional_info)

        # KRX 데이터와 Daum 데이터 결합
        combined_df = pd.concat([listed_companies_df.reset_index(drop=True), additional_info_df], axis=1)

        # 마켓타입이 "정보 없음"인 행 삭제
        combined_df = combined_df[combined_df['마켓타입'] != "정보 없음"]

        combined_df.columns = ["ticker","company_name","category","company_overview","market_cap","market_type"]
        # 결합된 DataFrame의 첫 몇 행 출력
        print("상장 기업 데이터의 첫 몇 행:")
        print(combined_df.head())

        # CSV 파일로 저장
        combined_df.to_csv("data/listed_companies_with_info.csv", index=False, encoding="utf-8-sig")
        print("CSV 파일로 저장되었습니다: listed_companies_with_info.csv")

        # 마지막 업데이트 시간 로그
        print(f"데이터가 마지막으로 업데이트된 시간: {datetime.now()}")
        return combined_df
    except Exception as e:
        print(f"오류 발생: {e}")
        return

if __name__ == '__main__':
    stock_info_crawler()