import time
import urllib3
from dotenv import load_dotenv
import os
import dart_fss
import pandas as pd
import requests
import zipfile
from zipfile import BadZipFile
import math
from bs4 import BeautifulSoup
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

def categorize_announcement_type(report_nm):
    """
    공시 제목(report_nm)을 기반으로 공시 타입을 분류합니다.

    Parameters:
        report_nm (str): 공시 제목

    Returns:
        str: 공시 타입 (ENUM 값)
    """
    if any(keyword in report_nm for keyword in ['사업보고서', '분기보고서', '반기보고서']):
        return '정기공시'
    elif any(keyword in report_nm for keyword in ['단일판매ㆍ공급계약체결', '주요사항보고서', '소송등의판결ㆍ결정']):
        return '주요사항보고'
    elif any(keyword in report_nm for keyword in ['감사보고서', '검토보고서']):
        return '외부감사관련'
    elif any(keyword in report_nm for keyword in ['증권신고서', '투자설명서', '발행조건확정']):
        return '발행공시'
    elif any(keyword in report_nm for keyword in ['주식등의대량보유상황보고서', '임원ㆍ주요주주특정증권등소유상황보고서']):
        return '지분공시'
    elif any(keyword in report_nm for keyword in ['자산유동화계획서', '자산유동화실적보고서']):
        return '자산유동화'
    elif any(keyword in report_nm for keyword in ['기업설명회(IR)개최', '시장조치결과']):
        return '거래소공시'
    elif '대규모내부거래관련사항' in report_nm:
        return '공정위공시'
    else:
        return '기타공시'

def fetch_dart_filings(bgn_de, end_de, corp_cls='Y', page_count=25, output_dir='disclosure'):
    """
    DART 공시 데이터를 수집하고 내용 추출 및 원문 URL 추가 후 CSV로 저장하는 함수.

    Parameters:
        bgn_de (str): 검색 시작일 (YYYYMMDD 형식).
        end_de (str): 검색 종료일 (YYYYMMDD 형식).
        corp_cls (str): 법인 구분 (Y: 유가증권, K: 코스닥, N: 코넥스, E: 기타).
        page_count (int): 페이지당 가져올 공시 수.
        output_dir (str): 결과를 저장할 디렉토리.
        csv_filename (str): 저장할 CSV 파일명.
    """
    # .env 파일 로드
    load_dotenv()

    # API 키 로드
    api_key = os.getenv("DART_API_KEY")
    dart_fss.set_api_key(api_key)

    # 첫 요청으로 total_count 확인
    first_request = dart_fss.api.filings.search_filings(
        bgn_de=bgn_de,
        end_de=end_de,
        corp_cls=corp_cls,
        last_reprt_at='N',
        sort='date',
        sort_mth='desc',
        page_no=1,
        page_count=page_count
    )

    # exit()
    # 총 데이터 수(total_count) 가져오기
    if 'total_count' in first_request:
        total_count = int(first_request['total_count'])
        total_pages = math.ceil(total_count / page_count)
        print(f"총 {total_count}개의 공시 데이터, {total_pages} 페이지 필요")
    else:
        print("total_count 정보를 가져올 수 없습니다.")
        return

    # 모든 공시 데이터를 저장할 리스트
    all_filings = []

    # 필요한 페이지 수만큼 반복
    for page_no in range(1, total_pages + 1):
        filings = dart_fss.api.filings.search_filings(
            bgn_de=bgn_de,
            end_de=end_de,
            corp_cls=corp_cls,
            last_reprt_at='N',
            sort='date',
            sort_mth='desc',
            page_no=page_no,
            page_count=page_count
        )

        if page_no % 100 == 0:
            print("change_api_key")
            time.sleep(60)
            dart_fss.set_api_key(api_key)

        if 'list' in filings and filings['list']:
            all_filings.extend(filings['list'])  # 공시 데이터를 리스트에 추가
            print(f"페이지 {page_no}: {len(filings['list'])}개 공시 가져옴")
        else:
            print(f"페이지 {page_no} 데이터가 없습니다.")

    # 모든 데이터를 DataFrame으로 변환
    df = pd.DataFrame(all_filings)
    print(f"총 {df.shape[0]}개의 공시 데이터를 수집했습니다.")

    df['announcement_type'] = df['report_nm'].apply(categorize_announcement_type)

    # 원문 URL 추가
    base_url = "https://dart.fss.or.kr/dsaf001/main.do?rcpNo="
    df['original_url'] = base_url + df['rcept_no']

    # 공시 내용을 가져와 content 열에 추가
    url = "https://opendart.fss.or.kr/api/document.xml"  # DART 문서 API 엔드포인트
    contents = []

    # 저장 경로 설정
    disclosure_dir = os.path.join(os.getcwd(), output_dir)
    os.makedirs(disclosure_dir, exist_ok=True)  # 디렉토리가 없으면 생성

    num = 0
    for index, row in df.iterrows():
        num +=1

        if num %100 == 0:
            time.sleep(100)
            print("change_api_key")
            dart_fss.set_api_key(api_key)

        rcept_no = row['rcept_no']
        params = {
            'crtfc_key': api_key,
            'rcept_no': rcept_no
        }




        # ZIP 파일 다운로드 경로
        doc_zip_path = os.path.join(disclosure_dir, f'{rcept_no}.zip')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        response = requests.get(url, params=params,verify=False)

        if response.status_code == 200:
            with open(doc_zip_path, 'wb') as fp:
                fp.write(response.content)

            # ZIP 파일 해제 및 XML 읽기
            try:
                with zipfile.ZipFile(doc_zip_path, 'r') as zp:
                    xml_filename = zp.namelist()[0]
                    with zp.open(xml_filename) as xml_file:
                        raw_content = xml_file.read().decode('utf-8')  # XML 내용 디코딩
                        # HTML 코드 제거: BeautifulSoup로 텍스트만 추출
                        soup = BeautifulSoup(raw_content, 'html.parser')
                        clean_content = soup.get_text(strip=True)  # HTML 태그 제거 후 텍스트 추출
                        contents.append(clean_content)
                print(f"공시 {rcept_no}: 내용 추가 완료")
            except BadZipFile as e:
                print(f"공시 {rcept_no}: ZIP 파일 에러 - {e}")
                contents.append(None)  # 실패한 경우 None 추가
            finally:
                # ZIP 파일 삭제
                os.remove(doc_zip_path)
                print(f"ZIP 파일 삭제 완료: {doc_zip_path}")
        else:
            print(f"공시 {rcept_no}: 문서 다운로드 실패 - 상태 코드 {response.status_code}")
            contents.append(None)

    # DataFrame에 content 열 추가
    df['content'] = contents

    # 결과 확인
    print(df[['rcept_no', 'content', 'original_url']].head())

    df = df.dropna(subset=['stock_code', 'content'])  # NaN 값 제거
    df = df[df['stock_code'].str.strip() != '']  # 빈 문자열 제거
    df = df[df['content'].str.strip() != '']  # content가 빈 문자열인 경우 제거

    return df
# 함수 호출 예시
# fetch_dart_filings('20241120', '20241120', corp_cls='Y', page_count=25, csv_filename='kospi_disclo.csv')
