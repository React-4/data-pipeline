import openai
import tiktoken
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os

# OpenAI API 키 설정
openai.api_key = os.getenv("GPT_API_KEY")


def extract_text_from_xml_or_html(file_path):
    """
    XML 또는 HTML 파일에서 텍스트를 추출하는 함수
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # <html> 태그가 포함된 경우 HTML로 처리
        if "<html" in content.lower():
            print("HTML 파일 감지, HTML 기반으로 텍스트 추출 중...")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator=" ").strip()
        else:
            print("XML 파일 감지, XML 기반으로 텍스트 추출 중...")
            tree = ET.parse(file_path)
            root = tree.getroot()
            text = " ".join(elem.text.strip() for elem in root.iter() if elem.text)

        return text

    except Exception as e:
        print(f"Error reading file: {e}")
        return ""


def calculate_token_count(text):
    """
    텍스트의 토큰 수를 계산하는 함수
    """
    encoding = tiktoken.encoding_for_model("gpt-4")
    return len(encoding.encode(text))


def divide_text_by_tokens(text, max_tokens=60000):
    """
    텍스트를 최대 max_tokens 기준으로 분할하는 함수
    """
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    divided_texts = []
    for i in range(0, len(tokens), max_tokens):
        chunk = tokens[i:i + max_tokens]
        divided_texts.append(encoding.decode(chunk))
    return divided_texts


def summarize_chunk(chunk):
    """
    GPT API를 이용해 각 텍스트 조각을 요약하는 함수
    """
    prompt = f"""
    아래는 공시의 일부 내용입니다. 이 내용을 간단히 요약해 주세요:
    {chunk}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # GPT 모델 선택
            messages=[
                {"role": "system", "content": "You are a concise financial summarizer."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,  # 요청당 최대 토큰 수
            temperature=0.5
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.OpenAIError as e:
        print(f"Error with GPT API: {e}")
        return "요약 실패"


def analyze_combined_summary(summary_texts):
    """
    합쳐진 요약을 기반으로 공시 요약, 호재, 악재, 평가 의견을 생성
    """
    combined_summary = "\n".join(summary_texts)
    prompt = f"""
    아래는 공시의 요약된 내용입니다. 이를 바탕으로 공시 내용 요약, 호재, 악재, 그리고 투자 의견을 도출해 주세요:
    {combined_summary}
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert financial analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000,
            temperature=0.7
        )
        return response['choices'][0]['message']['content'].strip()
    except openai.OpenAIError as e:
        print(f"Error with GPT API: {e}")
        return "분석 실패"


def main(file_path):
    
    """
    XML 또는 HTML 파일에서 텍스트를 추출하고 요약 및 분석하는 메인 함수
    """
    print("파일에서 텍스트를 추출 중...")
    text = extract_text_from_xml_or_html(file_path)
    if not text.strip():
        print("파일에서 텍스트를 추출하지 못했습니다.")
        return

    print("텍스트 길이 계산 중...")
    token_count = calculate_token_count(text)
    print(f"전체 토큰 수: {token_count}")

    print("텍스트를 60,000 토큰 기준으로 분할 중...")
    chunks = divide_text_by_tokens(text, max_tokens=60000)
    summaries = []
    for i, chunk in enumerate(chunks, 1):
        print(f"{i}/{len(chunks)} 요약 진행 중...")
        summaries.append(summarize_chunk(chunk))

    print("\n모든 요약이 완료되었습니다. 요약을 기반으로 분석 중...")
    analysis_result = analyze_combined_summary(summaries)
    if analysis_result:
        print("\n최종 분석 결과:")
        print(analysis_result)
        with open("summary/"+file_path[11:-4]+".txt", "w", encoding="utf-8") as f:
            f.write(analysis_result)
            f.close()
    else:
        print("GPT API를 통한 분석 실패.")


if __name__ == "__main__":
    # 파일 경로 입력
    for file_path in os.listdir('disclosure'):
        print(file_path)
        # file_path = "20241118900145.xml"  # 공시 XML 또는 HTML 파일 경로
        main('disclosure/'+file_path)

    #main('disclosure/20241118000008.xml')
        
      
    
































