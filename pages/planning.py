import os
import streamlit as st
import pandas as pd

# === 파일 경로 설정 ===
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STATIC_DIR = os.path.join(BASE_DIR, 'data', 'static_files')
BOD_FILE = os.path.join(STATIC_DIR, 'item_bod.xlsx')
SS_FILE  = os.path.join(STATIC_DIR, 'safety_stock.xlsx')
CP_FILE  = os.path.join(STATIC_DIR, 'control_panel.xlsx')


def run_planning_page(suffix_inputs: dict, filtered_df: pd.DataFrame, log):
    st.header("🗓 계획 분석")

    # 1) 사용자 질문 입력 및 표시
    user_q = st.chat_input("💬 질문을 입력하세요...")
    if not user_q:
        return

    with st.chat_message("user"):
        st.markdown(user_q)
    log("Supervisor Agent: Planning Agent 질문 접수")
    log("Supervisor Agent → Planning Agent 전달 중")
    log("Planning Agent: 질문 파싱 및 RAG에서 선택 중")

    def reply(txt: str):
        with st.chat_message("assistant"):
            st.markdown(txt)

    q = user_q.lower()
    suffix   = suffix_inputs.get('Mapping Model.Suffix', '').strip()
    division = suffix_inputs.get('Division', '').strip()

    # 2) Max SR vs Main SP
    if 'max sr' in q and 'main sp' in q:
        log("Planning Agent: Max SR vs Main SP 흐름 선택")

        # ▶ PSI 필터링 Preview
        df_preview = filtered_df[
            filtered_df.get('Category', '').isin(
                ['SP [R+F]', 'Max Shipping Request[R+F]']
            )
        ]
        st.subheader("📂 PSI 필터링 Preview")
        # 주차 컬럼 식별
        week26 = [c for c in df_preview.columns if '2025-05-26' in c]
        week12 = [c for c in df_preview.columns if '2025-05-12' in c]
        # 포맷 함수: 정수 플로트는 정수로, 그 외는 원본
        def fmt(x):
            return int(x) if isinstance(x, float) and x.is_integer() else x
        # 스타일 적용
        styled_preview = (
            df_preview
            .style
            .format(fmt)
            # 5/26 컬럼 전부 강조
            .applymap(
                lambda _: 'background-color: #FFE88F',
                subset=week26
            )
            # 5/12 컬럼은 Category=="Max Shipping Request[R+F]"인 행만 강조
            .apply(
                lambda row: [
                    'background-color: #FFE88F'
                    if (col in week12 and row.get('Category')=='Max Shipping Request[R+F]')
                    else ''
                    for col in row.index
                ],
                axis=1
            )
        )
        st.write(styled_preview, use_container_width=True)


        reply(
            """
📊 **분석 결과:**

1. **Max SR 수립 기준**
   - Max SR은 BOD 기준 Lead Time (4주)과 안전재고 기준 (1주)을 합쳐 수립되었습니다.
   - 이로 인해 **5주**의 offset이 발생합니다。

2. **Main SP 수립 기준**  
   - Main SP는 자재 제약·CAPA제약·BOD 기준정보를 반영한 선적 계획입니다。
   - BOD Start Date는 **2025-05-01**로 설정되어, 이후 제약을 반영해 **5/26주차**에 일괄 수립됩니다。
   - 앞서 수립된 **2025-05-01 수량:1150 + 2025-05-26 수량:200**을 2025-05-26주차에 합산하여 수량:1350이 수립됩니다。

✅ **결론 요약:**
Max SR은 이론적 수요 기반 수립, Main SP는 현실 제약을 반영한 실행 계획이므로
주차 간 차이는 시스템 설계상 정상입니다。
"""
        )
        log("Planning Agent: Max SR vs Main SP 답변 완료")

        # ▶ Item_BOD 시트 로드 & 필터
        try:
            df_bod = pd.read_excel(BOD_FILE)
            key_col = next((c for c in df_bod.columns if 'suffix' in c.lower()), None)
            sel_bod = df_bod[df_bod[key_col].astype(str).str.strip() == suffix] if key_col else pd.DataFrame()

            st.subheader("📂 Item_BOD 시트 (해당 모델)")
            if not sel_bod.empty:
                # 포맷 함수: 정수 플로트는 정수로, 그 외는 원본
                def fmt(x):
                    return int(x) if isinstance(x, float) and x.is_integer() else x

                # 강조할 컬럼 찾기
                highlight_cols = [
                    col for col in sel_bod.columns
                    if any(k in col.lower() for k in
                           ['ship', 'effective', 'manual start', 'mp based'])
                ]

                styled_bod = (
                    sel_bod
                    .style
                    .format(fmt)
                    .applymap(lambda _: 'background-color: #FFE88F', subset=highlight_cols)
                )
                st.write(styled_bod)

            else:
                st.dataframe(sel_bod, use_container_width=True)

        except Exception as e:
            st.error(f"Item_BOD 파일 로드 오류: {e}")

        # ▶ Safety_Stock 시트 로드 & 필터
        try:
            df_ss = pd.read_excel(SS_FILE)
            suffix_col = next((c for c in df_ss.columns if 'suffix' in c.lower()), None)
            sel_ss = df_ss[df_ss[suffix_col].astype(str).str.strip() == suffix] if suffix_col else pd.DataFrame()

            st.subheader("📂 Safety_Stock 시트 (해당 모델)")
            if not sel_ss.empty and 'Category' in sel_ss.columns:
                # 포맷 함수
                def fmt(x):
                    return int(x) if isinstance(x, float) and x.is_integer() else x

                # 강조할 5/26주차 컬럼 찾기
                week_col = next((c for c in sel_ss.columns if '2025-05-26' in c), None)

                styled_ss = (
                    sel_ss
                    .style
                    .format(fmt)
                    .apply(
                        lambda row: [
                            'background-color: #FFE88F' if (row['Category']=='Changed' and col==week_col) else ''
                            for col in sel_ss.columns
                        ],
                        axis=1
                    )
                )
                st.write(styled_ss)

            else:
                st.dataframe(sel_ss, use_container_width=True)

        except Exception as e:
            st.error(f"Safety_Stock 파일 로드 오류: {e}")

    # 3) BOD Start Date 설명
    elif 'bod start' in q:
        log("Planning Agent: BOD Start Date 관련 RAG에서 찾는 중")
        reply(
            "해당 모델의 Effective Date는 Start Date와 Manual Start Date중 가장 늦은 5/26으로 설정 되어있습니다。"
            "GPLM 시스템의 R&D PMS 메뉴에 등록된 개발일정이 GSCP Item BOD 페이지로 I/F되어 Item BOD의 BOD Start Date로 인식됩니다。"
        )
        log("Planning Agent: BOD Start Date 설명 완료")

                # ▶ Item_BOD 시트 로드 & 필터
        try:
            df_bod = pd.read_excel(BOD_FILE)
            key_col = next((c for c in df_bod.columns if 'suffix' in c.lower()), None)
            sel_bod = df_bod[df_bod[key_col].astype(str).str.strip() == suffix] if key_col else pd.DataFrame()

            st.subheader("📂 Item_BOD 시트 (해당 모델)")
            if not sel_bod.empty:
                # 포맷 함수: 정수 플로트는 정수로, 그 외는 원본
                def fmt(x):
                    return int(x) if isinstance(x, float) and x.is_integer() else x

                # 강조할 컬럼 찾기
                highlight_cols = [
                    col for col in sel_bod.columns
                    if any(k in col.lower() for k in
                           ['ship', 'effective', 'manual start', 'mp based'])
                ]

                styled_bod = (
                    sel_bod
                    .style
                    .format(fmt)
                    .applymap(lambda _: 'background-color: #FFE88F', subset=highlight_cols)
                )
                st.write(styled_bod)

            else:
                st.dataframe(sel_bod, use_container_width=True)

        except Exception as e:
            st.error(f"Item_BOD 파일 로드 오류: {e}")


    # 4) Delay Allocation 설명
    elif 'delay' in q:
        log("Planning Agent: Delay Allocation 관련 RAG에서 찾는 중")
        reply(
            "해당 Division은 **Delay Allocation** 로직이 **ON**으로 설정되어 있습니다。"
            "공급 계획이 지연 수립되어 Shortage 처리가 되지 않고、다음 Sales Allocation에 할당되는 기능입니다。"
        )
        log("Planning Agent: Delay Allocation 설명 완료")

        # ▶ Control_Panel 시트 로드 & 필터
        try:
            df_cp = pd.read_excel(CP_FILE)
            div_col = next((c for c in df_cp.columns if c.lower().startswith('division')), None)
            sel_cp = df_cp[df_cp[div_col].astype(str).str.strip() == division] if div_col else pd.DataFrame()

            st.subheader("📂 Control_Panel 시트 (해당 Division)")
            if not sel_cp.empty:
                def fmt(x):
                    return int(x) if isinstance(x, float) and x.is_integer() else x

                highlight_cols = [c for c in sel_cp.columns if 'delay' in c.lower() and 'alloc' in c.lower()]

                styled_cp = (
                    sel_cp
                    .style
                    .format(fmt)
                    .applymap(lambda _: 'background-color: #FFE88F', subset=highlight_cols)
                )
                st.write(styled_cp)
            else:
                st.dataframe(sel_cp, use_container_width=True)

        except Exception as e:
            st.error(f"Control_Panel 파일 로드 오류: {e}")

    # 5) 지원되지 않는 질문
    else:
        log("Planning Agent: 지원되지 않는 질문")
        reply("죄송합니다。해당 계획 분석 질문은 지원하지 않습니다。")
