# pages/trend.py
import re
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def run_trend_page(filtered_df: pd.DataFrame, log):
    st.header("🔍 트렌드 분석")
    st.write("분석할 행(주차)을 하나 선택한 뒤, 아래 🖥️ ‘분석 실행’ 버튼을 눌러주세요.")

    # —(1) AgGrid 세팅 (필터/정렬/리사이즈/체크박스 단일선택)
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_default_column(
        filter=True, sortable=True, resizable=True, flex=1, minWidth=80
    )
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    grid_opts = gb.build()

    grid_resp = AgGrid(
        filtered_df,
        gridOptions=grid_opts,
        height=350,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme="streamlit",
    )

    # —(2) 선택된 로우 → 리스트 강제 변환
    raw = grid_resp.get("selected_rows", None)
    if isinstance(raw, list):
        records = raw
    elif isinstance(raw, pd.DataFrame):
        records = raw.to_dict("records")
    else:
        records = []

    # —(3) 선택 안내 및 실행 대기
    if len(records) == 0:
        st.info("▶️ 먼저 체크박스로 한 개의 행을 선택해주세요.")
        return

        # 5) 분석 실행 버튼
    if not st.button("🖥️ 분석 실행"):
        return

    row = records[0]
    log("📈 트렌드 분석 시작")

    # 주차 컬럼 식별 및 정렬
    week_cols = sorted(
        [c for c in filtered_df.columns if re.search(r"\(W\d+\)", c)],
        key=lambda c: int(re.search(r"\(W(\d+)\)", c).group(1))
    )

    # 숫자형 값 추출
    data = {}
    for col in week_cols:
        try:
            data[int(re.search(r"\(W(\d+)\)", col).group(1))] = float(row[col])
        except:
            pass

    values = pd.Series(data).sort_index()
    avg_val = values.mean()
    st.markdown(f"**평균:** {avg_val:.2f}")

    pct = values.pct_change().mul(100).round(1)
    pct_df = pd.DataFrame({"주차": pct.index.astype(str), "변동률(%)": pct.values}).set_index("주차")
    st.markdown("**주차별 변동률 (%)**")
    st.dataframe(pct_df, use_container_width=True)

    # ─── Beautified Chart ────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))                   # 사이즈 키우기
    ax.plot(
        pct_df.index, pct_df["변동률(%)"],
        marker="o", markersize=8, linewidth=2
    )
    ax.set_title("주차별 변동률 추이", fontsize=16, pad=14)
    ax.set_ylabel("변동률 (%)", fontsize=12)
    ax.grid(True, linestyle="--", alpha=0.5)
    # y축 여유 줘서 데이터가 차트에 좀 더 들어오도록
    ymin, ymax = pct_df["변동률(%)"].min(), pct_df["변동률(%)"].max()
    pad = max(abs(ymin), abs(ymax)) * 0.1
    ax.set_ylim(ymin - pad, ymax + pad)

    # X축 레이블 가독성 높이기
    plt.xticks(rotation=45, fontsize=10)
    plt.tight_layout()

    st.pyplot(fig)
    log("📈 트렌드 분석 완료")

    # ─── 자동 코멘트 ────────────────────────────────────────────────
    if pct_df["변동률(%)"].isna().all():
        st.info("⚠️ 변동률을 계산할 데이터가 충분하지 않습니다.")
    else:
        most_drop = pct_df["변동률(%)"].idxmin()
        drop_val  = pct_df.loc[most_drop, "변동률(%)"]
        st.markdown(f"> **가장 큰 변동:** 주차 {most_drop}에 {drop_val:.1f}%로 급격히 변화했습니다.")