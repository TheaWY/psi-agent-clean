
import streamlit as st

def render_excel_summary(format_info):
    return [
        f"📄 이 문서는 **{format_info['title']}** 유형으로 인식되었습니다.",
        f"🔑 주요 열: `{', '.join(format_info['matched_columns'])}`",
        f"📊 신뢰도: **{format_info['confidence']:.0%}**"
    ]

def render_excel_preview(df, sheet_name="Sheet1"):
    st.markdown(f"#### 📄 `{sheet_name}` 시트 미리보기")
    st.dataframe(df.head(10), use_container_width=True)

def render_log(lines):
    st.sidebar.markdown("### 🔁 처리 로그")
    for line in lines:
        st.sidebar.markdown(f"• {line}")
