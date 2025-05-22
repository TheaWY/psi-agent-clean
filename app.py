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
st.markdown("""
<style>
  [data-testid="stSidebarNav"] { visibility: hidden !important; }
  .stButton > button {
    font-size:1.1rem !important;
    padding:12px 20px !important;
    margin:4px !important;
  }
</style>
""", unsafe_allow_html=True)

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
    if st.session_state.logs and st.session_state.logs[-1] == msg:
        return
    st.session_state.logs.append(msg)
    st.sidebar.markdown(f"• {msg}")
    time.sleep(0.05)

# ── 챗 스트림 컨테이너 초기화 ────────────────────────────────────────────────────
if "chat_box" not in st.session_state:
    st.session_state.chat_box = st.container()

def append_message(role: str, text: str):
    """chat_box 컨테이너에 메시지를 추가"""
    with st.session_state.chat_box:
        st.chat_message(role)(lambda: st.markdown(text))

# ── 챗 히스토리 초기화 ───────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── 화면 타이틀 & 기존 히스토리 복원 ─────────────────────────────────────────────
st.title("📦 PSI 분석 봇")
st.caption("LG전자 PSI 문의 대응용 Agentic AI 시스템")
for role, msg in st.session_state.history:
    append_message(role, msg)

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

    append_message("assistant", "**📄 업로드된 엑셀 미리보기**")
    append_message("assistant", df.head(5).to_markdown())

    log("File Agent: 시트 미리보기 완료")
    log("Supervisor Agent: 모델 필터링 단계 진입")

    # 키 입력 UI
    st.markdown("### 🔑 분석할 모델 키 값을 입력해주세요:")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        div    = st.text_input("Division")
        from_site = st.text_input("Rep From Site")
        suffix  = st.text_input("Mapping Model.Suffix")
    with c2:
        to_site = st.text_input("Site")
    if st.button("🔍 모델 확인"):
        log("Supervisor Agent → Model Agent: 모델 확인 요청")
        keys = {
            "Division": div,
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
            append_message("assistant", "✅ 해당 모델이 확인되었습니다.")
            append_message("assistant", match.to_markdown())
            log("Model Agent: 모델 필터링 완료, 결과 반환")
        else:
            append_message("assistant", "❌ 일치하는 모델을 찾을 수 없습니다.")
            log("Model Agent: 모델 필터링 실패")

# ── 2) 기능 메뉴 ────────────────────────────────────────────────────────────────
if st.session_state.get("model_selected"):
    log("Supervisor Agent: 기능 메뉴 표시")
    append_message("assistant", "### 🤖 무엇을 도와드릴까요?")
    cols = st.columns(4, gap="large")
    if cols[0].button("📘 단순 용어 문의"):
        log("Supervisor Agent → Term Agent: 라우팅")
        st.session_state.mode = "term"
    if cols[1].button("📊 실적 분석"):
        log("Supervisor Agent → Performance Agent: 라우팅")
        st.session_state.mode = "perf"
    if cols[2].button("🧮 계획 분석"):
        log("Supervisor Agent → Planning Agent: 라우팅")
        st.session_state.mode = "plan"
    if cols[3].button("📈 트렌드 분석"):
        log("Supervisor Agent → Trend Agent: 라우팅")
        st.session_state.mode = "trend"

# ── 3) 메인 채팅 입력 & 실행 ─────────────────────────────────────────────────────
user_q = st.chat_input("질문을 입력하세요…", key="main_chat")
if user_q:
    # 1) user 메시지 append
    append_message("user", user_q)
    st.session_state.history.append(("user", user_q))

    # 2) mode별 처리 & assistant 메시지 append
    mode = st.session_state.get("mode")
    if mode == "term":
        log("Term Agent: 단순 용어 문의 처리 시작")
        resp = run_term_page(st.session_state.model_selected, log, return_only=True)
        log("Term Agent: 처리 완료")
    elif mode == "perf":
        log("Performance Agent: 실적 분석 처리 시작")
        resp = run_performance_page(st.session_state.model_selected,
                                    st.session_state.filtered_df, log,
                                    return_only=True)
        log("Performance Agent: 처리 완료")
    elif mode == "plan":
        log("Planning Agent: 계획 분석 처리 시작")
        resp = run_planning_page(st.session_state.model_selected,
                                 st.session_state.filtered_df, log,
                                 return_only=True)
        log("Planning Agent: 처리 완료")
    elif mode == "trend":
        log("Trend Agent: 트렌드 분석 시작")
        resp = run_trend_page(st.session_state.filtered_df,
                              log, return_only=True)
        log("Trend Agent: 처리 완료")
    else:
        resp = "먼저 메뉴에서 기능을 선택해주세요."

    append_message("assistant", resp)
    st.session_state.history.append(("assistant", resp))
