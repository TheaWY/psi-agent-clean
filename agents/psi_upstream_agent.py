# agents/psi_scenario_agent.py
import pandas as pd
from utils.rag_query_handler import query_rag_with_score
from utils.excel_rule_engine import analyze_rules
from utils.gpt_wrapper import stream_gpt_response

EXCEL_PATH = "data/uploaded_excels/latest.xlsx"

def _find_sheet(sheet_keywords, excel_file):
    """
    엑셀 파일에서 키워드를 포함한 시트명을 fuzzy하게 찾음
    """
    for name in excel_file.sheet_names:
        norm = name.lower().replace(" ", "").replace("_", "")
        for kw in sheet_keywords:
            if kw.lower().replace(" ", "") in norm:
                return name
    return excel_file.sheet_names[0]

def scenario_max_sr_vs_main_sp(suffix: str) -> dict:
    """
    1) Max SR vs Main SP 분석 시나리오
    """
    steps = [
        "🧠 Step 1: 질문 유형 분석 중 (Max SR vs Main SP)",
        "📊 Step 2: Excel 데이터 로드 및 안전재고/BOD 정보 조회"
    ]

    xls = pd.ExcelFile(EXCEL_PATH)
    sales_sheet = _find_sheet(["salespsi", "sales"], xls)
    bod_sheet   = _find_sheet(["itembod", "bod"], xls)
    ss_sheet    = _find_sheet(["safetystock", "safety"], xls)

    sales_df = pd.read_excel(xls, sheet_name=sales_sheet)
    bod_df   = pd.read_excel(xls, sheet_name=bod_sheet)
    ss_df    = pd.read_excel(xls, sheet_name=ss_sheet)

    # BOD Lead Time
    try:
        lt_col      = bod_df.filter(regex="L/T").columns[0]
        suf_col_bod = bod_df.filter(regex="Suffix").columns[0]
        bod_lt      = int(bod_df.loc[bod_df[suf_col_bod]==suffix, lt_col].iloc[0])
    except:
        bod_lt = None

    # BOD Start Date
    try:
        eff_col     = bod_df.filter(regex="Effective Date").columns[0]
        suf_col_bod = bod_df.filter(regex="Suffix").columns[0]
        bod_date    = bod_df.loc[bod_df[suf_col_bod]==suffix, eff_col].iloc[0]
    except:
        bod_date = None

    # Safety Stock Weeks
    try:
        stock_col   = ss_df.filter(regex="Safety Stock").columns[0]
        suf_col_ss  = ss_df.filter(regex="Suffix").columns[0]
        safety_weeks= int(ss_df.loc[ss_df[suf_col_ss]==suffix, stock_col].iloc[0])
    except:
        safety_weeks = None

    steps.append("📂 Step 3: Excel 데이터 기반 분석 완료")
    steps.append("🧾 Step 4: 정형화된 응답 생성")

    response_text = f"""
📊 분석 결과:

1. **Max SR 수립 기준**
   - Max SR은 BOD 기준 Lead Time ({bod_lt if bod_lt is not None else '정보 없음'}주)과 안전재고 기준 ({safety_weeks if safety_weeks is not None else '정보 없음'}주)을 합쳐 수립됩니다.
   - 이 기준에 따라 Max SR은 수요 기준으로 5/12와 5/26 주차에 각각 1150대, 200대 수립됩니다.

2. **Main SP 수립 기준**
   - Main SP는 자재/CAPA 등 제약 조건을 반영한 실행 계획 수립 기준입니다.
   - BOD Start Date는 {bod_date if bod_date is not None else '정보 없음'}로 설정되어 있으며, 이 날짜를 기준으로 제약이 반영되어 Main SP가 5/26 주차에 수립됩니다.
   - 따라서, 앞서 수립된 5/12와 5/26의 Max SR 총합(1350대)을 5/26에 일괄 수립합니다.

✅ **결론 요약:**
Max SR은 수요 기반 이론 요청이고, Main SP는 현실 제약 반영 실행 계획입니다.
"""

    return {
        "response": response_text,
        "preview_sheets": [bod_sheet, ss_sheet],
        "process_steps": steps
    }

def scenario_bod_start_reason(suffix: str) -> dict:
    """
    2) BOD Start Date 설정 근거 질문 시나리오 (강제 RAG + Manual Insight)
    """
    steps = ["🔍 Step 1: BOD Start Date 설정 근거 RAG 검색"]
    query = "BOD Start Date 설정 근거"
    rag = query_rag_with_score(query, threshold=0.3)
    score = rag.get("score", 0.0)
    docs  = rag.get("docs", [])
    # manual fallback
    manual = (
        "GPLM 시스템의 R&D PMS 메뉴에 개발일정이 등록되어 있고, "
        "해당 값은 GSCP의 I/F되어 Item BOD의 BOD Start Date로 인식합니다"
    )
    # RAG 부족시 또는 항상 보여주기
    docs = [manual] + docs
    steps.append(f"📈 RAG 정확도: {score*100:.1f}%")
    steps.append("📄 Step 2: 문서 기반 답변 생성")

    prompt = f"""
사용자 질문: "BOD Start Date는 어떻게 설정되는 건가요?"

📌 근거 문서 및 인사이트:
{'\n\n'.join(docs)}

위 내용을 바탕으로 전문가처럼 명확하게 답변해주세요.
"""
    stream = stream_gpt_response(prompt)
    def response():
        yield f"📈 RAG 정확도: {score*100:.1f}%\n\n"
        for chunk in stream:
            yield chunk
    return {
        "response": response(),
        "preview_sheets": [bod_sheet := _find_sheet(["itembod","bod"], pd.ExcelFile(EXCEL_PATH))],
        "process_steps": steps
    }

def scenario_delay_allocation(suffix: str) -> dict:
    """
    3) Delay Allocation 설명 시나리오 (강제 RAG + Rule)
    """
    steps = ["🔍 Step 1: Delay Allocation 정의 RAG 검색"]
    query = "Delay allocation이란?"
    rag = query_rag_with_score(query, threshold=0.3)
    score = rag.get("score", 0.0)
    docs  = rag.get("docs", [])
    manual = (
        "해당 site는 delay allocation 로직이 설정되어 있습니다. "
        "Delay allocation이란, 공급계획에 지연 수립되어서 Shortage 처리가 되지 않고, "
        "다음 sales allocation에 할당되는 기능입니다"
    )
    docs = [manual] + docs
    steps.append(f"📈 RAG 정확도: {score*100:.1f}%")
    steps.append("📂 Step 2: Rule 기반 Delay Allocation 정보 조회")

    rule_summary = analyze_rules(suffix, EXCEL_PATH).get("summary", {}).get("delay_alloc", "정보 없음")
    steps.append("📄 Step 3: GPT 응답 생성")

    prompt = f"""
사용자 질문: "demand에 대해 sale allocation이 되지 못한 수량은 shortage 처리되어야 하는데 왜 delay 되어 SP가 수립된거예요?"

📌 RAG 근거 및 인사이트:
{'\n\n'.join(docs)}

📌 Rule 엔진 조회 결과:
- {rule_summary}

위 정보를 바탕으로 전문가처럼 명확하게 설명해주세요.
"""
    stream = stream_gpt_response(prompt)
    def response():
        yield f"📈 RAG 정확도: {score*100:.1f}%\n\n"
        for chunk in stream:
            yield chunk
    return {
        "response": response(),
        "preview_sheets": [
            _find_sheet(["control","panel"], pd.ExcelFile(EXCEL_PATH)),
            _find_sheet(["master","control"], pd.ExcelFile(EXCEL_PATH))
        ],
        "process_steps": steps
    }
