import re
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def run_trend_page(filtered_df: pd.DataFrame, log):
    # 페이지 헤더 및 안내
    st.header("🔍 트렌드 분석")
    st.write("분석할 행(주차)을 하나 선택한 뒤, 아래 🖥️ ‘분석 실행’ 버튼을 눌러주세요.")
    st.info("▶️ 체크박스로 한 개의 행을 선택해주세요.")

    # 1) AgGrid 설정
    gb = GridOptionsBuilder.from_dataframe(filtered_df)
    gb.configure_default_column(filter=True, sortable=True, resizable=True, flex=1, minWidth=80)
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    grid_opts = gb.build()
    grid_resp = AgGrid(
        filtered_df,
        gridOptions=grid_opts,
        height=350,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        theme="streamlit"
    )

    # 2) 선택된 로우 리스트 변환
    raw = grid_resp.get("selected_rows", [])
    if isinstance(raw, pd.DataFrame):
        records = raw.to_dict("records")
    else:
        records = raw
    if not records:
        return

    # 3) 분석 실행 버튼
    if not st.button("🖥️ 분석 실행"):
        return

    row = records[0]
    log("📈 트렌드 분석 시작")

    # 4) 주차 컬럼 추출 및 정렬
    week_cols = sorted(
        [c for c in filtered_df.columns if re.search(r"\(W\d+\)", c)],
        key=lambda c: int(re.search(r"\(W(\d+)\)", c).group(1))
    )

    # 5) 값 추출 및 변동률 계산
    data = {}
    for col in week_cols:
        try:
            val = row.get(col, 0)
            num = float(val) if val not in (None, "", "None") else 0.0
        except:
            num = 0.0
        week = int(re.search(r"\(W(\d+)\)", col).group(1))
        data[week] = num
    values = pd.Series(data).sort_index()
    avg_val = values.mean()

    pct = values.pct_change().mul(100).round(1)
    pct = pct.replace([np.inf, -np.inf], np.nan)
    valid = pct.dropna()
    if valid.empty:
        st.warning("⚠️ 변동률을 계산할 데이터가 충분하지 않습니다.")
        return

    # 6) 결과 렌더링 (평균, 표, 그래프)
    col1, col2 = st.columns([1,1])
    with col1:
        st.markdown(f"**평균:** {avg_val:.2f}")
        pct_df = pd.DataFrame({"Week": valid.index.astype(str), "Change %": valid.values}).set_index("Week")
        st.markdown("**주차별 변동률 (%)**")
        st.dataframe(pct_df, use_container_width=True)
    with col2:
        fig, ax = plt.subplots(figsize=(6,3))
        ax.plot(valid.index.astype(str), valid.values, marker="o", markersize=6, linewidth=2)
        ax.set_xlabel("Week", fontsize=12)
        ax.set_ylabel("Change %", fontsize=12)
        ax.set_frame_on(False)
        ax.grid(True, linestyle="--", alpha=0.5)
        ymin, ymax = valid.min(), valid.max()
        pad = max(abs(ymin), abs(ymax)) * 0.1
        ax.set_ylim(ymin - pad, ymax + pad)
        plt.xticks(rotation=45, fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)

    log("📈 트렌드 분석 완료")

    # 7) 자동 코멘트
    most_drop = valid.idxmin()
    drop_val = valid.loc[most_drop]
    st.markdown(f"> **가장 큰 변동:** Week {most_drop}에 {drop_val:.1f}%로 급격히 변화했습니다.")
