import requests
import zipfile
import os
from bs4 import BeautifulSoup
from zipfile import BadZipFile

# 크롤링
url = 'https://dart.fss.or.kr/dsac001/mainAll.do'
response = requests.get(url)  # GET 메소드를 사용하여 url에 HTTP Request 전송


# BeautifulSoup 객체 생성
soup = BeautifulSoup(response.content, 'html.parser')

# 모든 <td> 태그 선택
td_elements = soup.select('tbody tr td')

# 각 <td> 태그 내 <a> 태그의 id 값 추출
a_ids = []
for td in td_elements:
    a_tag = td.find('a')  # <td> 안의 첫 번째 <a> 태그 찾기
    if a_tag and 'id' in a_tag.attrs:  # <a> 태그와 id 속성 확인
        a_ids.append(a_tag['id'][2:])                                  


# # xml 추출
url="https://opendart.fss.or.kr/api/document.xml"
api_key=os.getenv("DART_API_KEY")
os.chdir('/Users/goeunpark/Desktop/gpt/disclosure') # 압축할 파일이 있는 경로


for no in a_ids:
    print(no)
    rcept_no=no
    params={
        'crtfc_key': api_key,
        'rcept_no': rcept_no
    }

    doc_zip_path=os.path.abspath('./document.zip')
    response=requests.get(url, params=params)
    with open(doc_zip_path, 'wb') as fp:
        fp.write(response.content)
    try: 
        zp=zipfile.ZipFile(doc_zip_path)
        zp.extractall()
    except BadZipFile as e : 
        print(f"에러: {e}")