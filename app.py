import os
import sys
import time
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# ── 페이지 모듈 경로 설정 ─────────────────────────────────────────────────────────
PAGES_DIR = os.path.join(os.path.dirname(__file__), "pages")
if PAGES_DIR not in sys.path:
    sys.path.append(PAGES_DIR)

from pages.planning    import run_planning_page
from pages.term        import run_term_page
from pages.performance import run_performance_page
from pages.trend       import run_trend_page

# ── 초기 설정 ────────────────────────────────────────────────────────────────────
load_dotenv()
st.set_page_config(page_title="📦 PSI 분석 봇", layout="wide")

# ── 전역 CSS ─────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
      /* 사이드바 숨기기 */
      [data-testid="stSidebarNav"] { visibility: hidden !important; }
      /* 버튼 크게, 간격 늘리기 */
      .stButton > button {
        font-size:1.1rem !important;
        padding:12px 20px !important;
        margin:4px !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 업로드 디렉토리 ─────────────────────────────────────────────────────────────
EXCEL_DIR  = os.path.join(os.getcwd(), "data", "uploaded_excels")
EXCEL_PATH = os.path.join(EXCEL_DIR, "latest.xlsx")
os.makedirs(EXCEL_DIR, exist_ok=True)

# ── 로그 초기화 ─────────────────────────────────────────────────────────────────
if "logs" not in st.session_state:
    st.session_state.logs = []
    st.sidebar.markdown("### 🔁 처리 로그")

def log(msg: str, reset: bool = False):
    if reset:
        st.session_state.logs = []
        st.sidebar.empty()
        st.sidebar.markdown("### 🔁 처리 로그")
    # 중복 방지
    if st.session_state.logs and st.session_state.logs[-1] == msg:
        return
    st.session_state.logs.append(msg)
    st.sidebar.markdown(f"• {msg}")
    time.sleep(0.05)

# ── 챗 히스토리 초기화 ───────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── 화면 타이틀 & 히스토리 ───────────────────────────────────────────────────────
st.title("📦 PSI 분석 봇")
st.caption("LG전자 PSI 문의 대응용 Agentic AI 시스템")
for role, content in st.session_state.history:
    with st.chat_message(role):
        st.markdown(content)

# ── 1) 엑셀 업로드 ───────────────────────────────────────────────────────────────
with st.sidebar:
    uploaded = st.file_uploader("📎 Excel 파일 업로드", type="xlsx")

if uploaded:
    log("Supervisor Agent: Excel 업로드 감지", reset=True)
    log("File Agent: 업로드 처리 시작")

    with open(EXCEL_PATH, "wb") as f:
        f.write(uploaded.getbuffer())
    log("File Agent: Excel 파일 저장 완료")

    log("File Agent → Supervisor Agent: 시트 로드 요청")
    df = pd.read_excel(EXCEL_PATH)
    st.session_state.df_sales = df
    log("File Agent: sales_psi 시트 로드 완료")

    with st.chat_message("assistant"):
        st.markdown("**📄 업로드된 엑셀 미리보기**")
        st.dataframe(df.head(5), use_container_width=True)
    log("File Agent: 시트 미리보기 완료")

    # 모델 키 입력
    log("Supervisor Agent: 모델 필터링 단계 진입")
    st.markdown("### 🔑 분석할 모델 키 값을 입력해주세요:")
    c1, c2, c3 = st.columns(3)
    with c1:
        div    = st.text_input("Division")
        region = st.text_input("Region")
    with c2:
        subs      = st.text_input("Subsidiary")
        from_site = st.text_input("Rep From Site")
    with c3:
        to_site = st.text_input("Site")
        suffix  = st.text_input("Mapping Model.Suffix")

    if st.button("🔍 모델 확인"):
        log("Supervisor Agent → Model Agent: 모델 확인 요청")
        keys = {
            "Division": div,
            "Region": region,
            "Subsidiary": subs,
            "Rep From Site": from_site,
            "Site": to_site,
            "Mapping Model.Suffix": suffix,
        }
        mask = pd.Series(True, index=df.index)
        for k, v in keys.items():
            mask &= df[k].astype(str).str.strip().eq(v.strip())
        match = df[mask]
        if not match.empty:
            st.session_state.model_selected = keys
            st.session_state.filtered_df   = match
            st.success("✅ 해당 모델이 확인되었습니다.")
            st.dataframe(match.head(3), use_container_width=True)
            log("Model Agent: 모델 필터링 완료, 결과 반환")
        else:
            st.error("❌ 일치하는 모델을 찾을 수 없습니다.")
            log("Model Agent: 모델 필터링 실패")

# ── 2) 기능 메뉴 ────────────────────────────────────────────────────────────────
if st.session_state.get("model_selected"):
    log("Supervisor Agent: 기능 메뉴 표시")
    st.markdown("### 🤖 무엇을 도와드릴까요?")
    col1, col2, col3, col4 = st.columns(4, gap="large")
    with col1:
        if st.button("📘 단순 용어 문의"):
            log("Supervisor Agent → Term Agent: 라우팅")
            st.session_state.mode = "term"
    with col2:
        if st.button("📊 실적 분석"):
            log("Supervisor Agent → Performance Agent: 라우팅")
            st.session_state.mode = "perf"
    with col3:
        if st.button("🧮 계획 분석"):
            log("Supervisor Agent → Planning Agent: 라우팅")
            st.session_state.mode = "plan"
    with col4:
        if st.button("📈 트렌드 분석"):
            log("Supervisor Agent → Trend Agent: 라우팅")
            st.session_state.mode = "trend"

# ── 3) 모드별 실행 ───────────────────────────────────────────────────────────────
mode = st.session_state.get("mode")

if mode == "term":
    log("Term Agent: 단순 용어 문의 처리 시작")
    run_term_page(st.session_state.model_selected, log)
    log("Term Agent: 단순 용어 문의 처리 완료")

elif mode == "perf":
    log("Performance Agent: 실적 분석 처리 시작")
    # ← 여기에 log 인자 추가!
    run_performance_page(
        st.session_state.model_selected,
        st.session_state.filtered_df,
        log
    )
    log("Performance Agent: 실적 분석 처리 완료")

elif mode == "plan":
    log("Planning Agent: 계획 분석 처리 시작")
    run_planning_page(
        st.session_state.model_selected,
        st.session_state.filtered_df,
        log
    )
    log("Planning Agent: 계획 분석 처리 완료")

elif mode == "trend":
    log("Trend Agent: 트렌드 분석 시작")
    run_trend_page(
        st.session_state.filtered_df,
        log
    )
    log("Trend Agent: 트렌드 분석 완료")
    log("Supervisor Agent: 분석 결과 검토 및 전달")
