# pages/term.py
import streamlit as st
from utils.rag_query_handler import query_docs, openai_completion

def run_term_page(model_selected: dict, log):
    st.markdown("## 📘 단순 용어 문의")
    st.info("추가 기능으로 엘지니와 연결될 예정입니다.")

    # 1) 사용자 입력
    user_input = st.text_input("궁금하신 용어를 입력하세요")
    if not user_input:
        return
    if st.button("전송"):
        log("Term Agent: 용어 문의 접수")

        # 2) RAG 검색
        docs, confidence = query_docs(user_input)
        st.markdown(f"- **RAG confidence:** {confidence:.2f} ({'양호' if confidence>=0.3 else '유사도 기준 미달'})")
        st.markdown("🔍 **검색된 문서 일부:**")
        for d in docs[:3]:
            st.write(f"> {d[:200]}…")

        # 3) 답변 생성
        if confidence >= 0.3:
            # 일반 RAG 기반 답변
            prompt = f"다음 참고 문서를 보고 '{user_input}'을(를) SCM-PSI(Planning, Sales, Inventory) 관점에서 설명해주세요:\n\n" + "\n\n".join(docs)
            answer = openai_completion(prompt)
            log("Term Agent: RAG 기반 답변 생성")
        else:
            # fallback: 무조건 SCM-PSI 관점 강제
            fallback_prompt = (
                f"RAG confidence가 낮으므로, '{user_input}' 용어를 반드시 "
                "Supply Chain Management의 PSI(Planning, Sales, Inventory) 관점에서만 설명해주세요.\n"
                "간단 명료하게 3개 항목으로 정리해 주세요."
            )
            answer = openai_completion(fallback_prompt)
            log("Term Agent: GPT fallback(PSI 도메인) 답변 생성")

        # 4) 답변 출력
        with st.chat_message("assistant"):
            st.markdown(answer)
