import openai
import tiktoken
import os
import pandas as pd
from bs4 import BeautifulSoup
import time

# OpenAI API 키 설정
openai.api_key = os.getenv("GPT_API_KEY")


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


def process_disclosures(disclosure_df, stock_info_df, output_path="result_table.csv"):
    """
    disclosure_df의 content를 GPT로 요약하고 결과를 테이블로 저장하는 함수
    """
    # stock_code와 ticker를 매핑하여 stock_id 추가
    ticker_to_id = stock_info_df.set_index('ticker')['stock_id'].to_dict()
    disclosure_df['stock_id'] = disclosure_df['stock_code'].map(ticker_to_id)

    results = []
    for idx, row in disclosure_df.iterrows():
        stock_id = row['stock_id']
        content = row['content']
        if not isinstance(content, str) or not content.strip():
            # print(f"행 {idx}: 내용이 비어있음. 건너뜀.")
            continue

        # print(f"Stock ID {stock_id}, 행 {idx} 처리 중...")

        # 텍스트 분할
        chunks = divide_text_by_tokens(content, max_tokens=60000)
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            # print(f"{i}/{len(chunks)} 요약 진행 중...")
            summaries.append(summarize_chunk(chunk))

        # 요약 분석
        print("\n모든 요약 완료. 분석 시작...")
        analysis_result = analyze_combined_summary(summaries)

        # 결과 저장
        result = {
            "stock_id": stock_id,
            "title": row.get("report_nm", ""),
                "content":analysis_result,
            "announcement_date": row.get("rcept_dt", ""),
            "submitter": row.get("flr_nm", ""),
            "original_announcement_url": row.get("original_url", ""),
            "announcement_type": row.get("announcement_type", ""),
        }
        results.append(result)

    # 결과를 DataFrame으로 변환
    result_df = pd.DataFrame(results)
    print(f"최종 결과 테이블 생성 완료: 총 {len(result_df)}개의 공시 데이터")

    # CSV로 저장
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    # print(f"결과 테이블 저장 완료: {output_path}")


def process_disclosures2(disclosure_df, stock_info_df):
    """
    disclosure_df의 content를 GPT로 요약하고 결과를 테이블로 저장하는 함수
    """
    # stock_code와 ticker를 매핑하여 stock_id 추가
    ticker_to_id = stock_info_df.set_index('ticker')['stock_id'].to_dict()
    disclosure_df['stock_id'] = disclosure_df['stock_code'].map(ticker_to_id)
    results = []
    print("공시 chatgpt 분석 시작",len(disclosure_df))

    for idx, row in disclosure_df.iterrows():
        stock_code = row['stock_code']
        stock_id = row['stock_id']
        content = row['content']

        # if stock_code == '005930':
        if not isinstance(content, str) or not content.strip():
            # print(f"행 {idx}: 내용이 비어있음. 건너뜀.")
            continue

        # print(f"Stock ID {stock_id}, 행 {idx} 처리 중...")

        # 텍스트 분할
        chunks = divide_text_by_tokens(content, max_tokens=60000)
        summaries = []
        for i, chunk in enumerate(chunks, 1):
            # print(f"{i}/{len(chunks)} 요약 진행 중...")
            summaries.append(summarize_chunk(chunk))

        # 요약 분석
        print("\n모든 요약 완료. 분석 시작...")
        analysis_result = analyze_combined_summary(summaries)
        # else:
        #     # print(f"Stock Code {stock_code}, 행 {idx}: ChatGPT 생략, 'test' 추가")
        #     analysis_result = "test"

        # 결과 저장
        result = {
            "stock_id": stock_id,
            "title": row.get("report_nm", ""),
            "content": analysis_result,
            "announcement_date": row.get("rcept_dt", ""),
            "submitter": row.get("flr_nm", ""),
            "original_announcement_url": row.get("original_url", ""),
            "announcement_type": row.get("announcement_type", ""),
        }
        results.append(result)

    # 결과를 DataFrame으로 변환
    result_df = pd.DataFrame(results)
    print(f"최종 결과 테이블 생성 완료: 총 {len(result_df)}개의 공시 데이터")

    return result_df
