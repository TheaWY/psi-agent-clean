# agents/supervisor_agent.py

import pandas as pd
from utils.rag_query_handler import query_rag_with_score
from agents.term_agent import term_agent
from agents.psi_analysis_agent import analyze_psi
from agents.query_agent import query_database
from agents.tracking_agent import track_psi_component
from agents.excel_agent import explain_with_item_bod_if_needed
from utils.gpt_wrapper import ask_gpt, stream_gpt_response

PSI_QUESTION_GUIDE = """
📌 다음과 같은 PSI 관련 질문을 하실 수 있어요:

- Max SR, Main SP, 구성요소 조건에 따른 실적 및 계획 해석
- PSI 분석을 위한 Master Data / Dynamic Query 연계
- PSI 결과의 Trend 분석 또는 원인 추적
"""

def supervisor_agent(user_query: str, log):
    """
    supervisor_agent: 사용자의 질문을 받아
    적절한 하위 에이전트로 라우팅하고,
    필요시 RAG → fallback 흐름을 관리합니다.
    """
    # 1) 사용자 질문 수신
    log("[Supervisor Agent] 사용자 질문 수신", reset=True)

    # 2) 잡담/유효 질문 분류
    log("[Supervisor Agent] 잡담 여부 판단 중…")
    if ask_gpt(f"잡담 판단: {user_query}").strip().upper().startswith("YES"):
        log("[Supervisor Agent] 잡담으로 분류됨")
        return {
            "agent": "System",
            "response": (
                "😊 안녕하세요! 저는 PSI 문의 전용 AI 에이전트입니다.\n"
                "도움이 필요한 PSI 관련 질문이 있으시면 알려주세요.\n\n"
                f"{PSI_QUESTION_GUIDE}"
            ),
            "process_steps": []
        }

    log("[Supervisor Agent] PSI 관련 질문인지 판단 중…")
    if not ask_gpt(f"PSI 질문 필터: {user_query}").strip().upper().startswith("YES"):
        log("[Supervisor Agent] PSI 질문 아님으로 분류")
        return {
            "agent": "System",
            "response": (
                "🤖 이 시스템은 PSI 수치, Max SR, 구성요소 추적 등과 관련된 질문에 응답합니다.\n\n"
                f"{PSI_QUESTION_GUIDE}"
            ),
            "process_steps": []
        }

    # 3) 복합 Excel + BOD 분석 필요 여부
    log("[Supervisor Agent] Excel+BOD 복합 분석 필요 여부 판단 중…")
    explanation = explain_with_item_bod_if_needed(user_query, "data/uploaded_excels/latest.xlsx")
    if explanation:
        log("[Supervisor Agent] Excel+BOD 분석 적용")
        return {
            "agent": "Excel+BOD Agent",
            "response": explanation,
            "process_steps": ["Excel+BOD 기반 복합 분석 실행"]
        }

    # 4) RAG 기반 검색
    log("[Supervisor Agent] RAG 유사도 검색 실행 중…")
    rag_result = query_rag_with_score(user_query, threshold=0.3)
    score = rag_result.get("score", 0.0)
    log(f"[Supervisor Agent] RAG 검색 완료 (score={score:.2f})")

    if rag_result.get("is_confident") and rag_result.get("docs"):
        docs = rag_result["docs"]
        context = "\n\n".join(docs)
        prompt = f"""
        당신은 LG전자 SCM PSI 매뉴얼 전문가입니다.

        아래는 검색된 문서 발췌입니다:
        {context}

        💬 사용자 질문: {user_query}

        위 문서를 바탕으로 구체적으로 답변해 주세요.
        """
        log("[Supervisor Agent] 문서 기반 응답 생성 중…")
        stream = stream_gpt_response(prompt)
        log("[Supervisor Agent] 문서 기반 응답 생성 완료")
        return {
            "agent": "RAG Agent",
            "response": stream,
            "process_steps": [f"RAG 기반 응답 (score={score:.2f})"]
        }

    # 5) Fallback: 기존 에이전트 순차 호출
    log("[Supervisor Agent] RAG 자신감 부족, Fallback 에이전트 호출 중…")
    fallback_agents = [
        (term_agent,        "Term Agent"),
        (analyze_psi,       "PSI Analysis Agent"),
        (query_database,    "Database Query Agent"),
        (track_psi_component, "Tracking Agent")
    ]
    for fn, name in fallback_agents:
        log(f"[Supervisor Agent] {name} 호출 중…")
        resp = fn(user_query)
        if resp:
            log(f"[Supervisor Agent] {name} 응답 수신")
            return {
                "agent": name,
                "response": resp,
                "process_steps": [f"{name} 처리"]
            }

    # 6) 실패 시 기본 안내
    log("[Supervisor Agent] 모든 에이전트 실패, 기본 안내 반환")
    return {
        "agent": "System",
        "response": (
            "죄송합니다. 요청하신 내용을 처리하지 못했습니다.\n\n"
            f"{PSI_QUESTION_GUIDE}"
        ),
        "process_steps": []
    }
