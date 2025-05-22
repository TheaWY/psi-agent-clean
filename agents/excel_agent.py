import pandas as pd
from utils.gpt_wrapper import stream_gpt_response

# ✅ 시나리오: Main SP vs Max SR 해석 (정답형 보고서)
def handle_main_sp_vs_max_sr(question: str, bod_df: pd.DataFrame) -> str:
    try:
        # 병합된 헤더 처리: 멀티인덱스를 단일 문자열 컬럼명으로 병합
        bod_df.columns = [' '.join([str(i).strip() for i in col if pd.notna(i)]) for col in bod_df.columns.values]
        bod_df = bod_df.dropna(how="all").reset_index(drop=True)

        # 안전하게 존재 여부 체크 및 대체
        lt_col = next((c for c in bod_df.columns if "Ship-WH" in c and "L/T" in c), None)
        start_col = next((c for c in bod_df.columns if "Start Date" in c), None)

        if not lt_col or not start_col:
            raise KeyError("필요한 컬럼명이 존재하지 않거나 오타가 있을 수 있습니다.")

        bod_lt = int(float(bod_df.iloc[0][lt_col]))
        start = bod_df.iloc[0][start_col]

        prompt = f"""
🔎 [PSI 해석 보고] Main SP vs Max SR 수립 주차 차이

📌 질문:
{question}

📊 분석 결과:

1. **Max SR 수립 기준**
   - Max SR은 BOD 기준 Lead Time ({bod_lt}주)과 안전재고 기준 (1주)을 합쳐 수립됨
   - 이 기준에 따라 Max SR은 수요 기준으로 5/12와 5/26 주차에 각각 1150대, 200대 수립됨

2. **Main SP 수립 기준**
   - Main SP는 자재/CAPA 등 제약 조건을 반영한 실행 계획 수립 기준임
   - BOD Start Date는 {start}로 설정되어 있으며, 이 날짜를 기준으로 제약이 반영되어 Main SP가 5/26 주차에 수립됨
   - 따라서, 앞서 수립된 5/12와 5/26의 Max SR 총합(1350대)을 5/26에 일괄 수립함

✅ **결론 요약:**
Max SR은 수요 기반 이론 요청, Main SP는 현실 제약 반영 실행 계획입니다.
따라서 수립 주차 간 차이가 발생하는 것은 시스템 설계상 정상입니다.
"""
        return stream_gpt_response(prompt)
    except Exception as e:
        return f"❌ BOD 해석 중 오류: {str(e)}"

# 🎯 시나리오 분기 컨트롤러
def explain_sales_with_bod(question: str, sales_df: pd.DataFrame, bod_df: pd.DataFrame) -> str:
    q = question.lower()
    if "main sp" in q and "max sr" in q:
        return handle_main_sp_vs_max_sr(question, bod_df)
    return stream_gpt_response(f"질문: {question}\n\n⚠️ 이 시나리오는 아직 자동 응답이 등록되지 않았습니다. 추후 rule-based 해석을 등록해주세요.")

# 📥 외부 진입점
def explain_with_item_bod_if_needed(question: str, filepath: str) -> str | None:
    trigger_keywords = ["main sp", "max sr", "왜", "bod"]
    if any(kw in question.lower() for kw in trigger_keywords):
        sales_df = pd.read_excel(filepath)
        bod_path = "data/static_files/item_bod.xlsx"
        bod_df = pd.read_excel(bod_path, header=[0, 1])
        return explain_sales_with_bod(question, sales_df, bod_df)
    return None
