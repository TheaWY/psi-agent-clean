import json
import os
from utils.chat_completion import stream_chat_completion
from utils.gpt_wrapper import ask_gpt

# ✅ PSI 슬라이드 청크 JSON 불러오기
PSI_CHUNK_PATH = "data/rag_chunks/psi_slide_chunks.json"
with open(PSI_CHUNK_PATH, "r", encoding="utf-8") as f:
    psi_chunks = json.load(f)

# ✅ GPT 기반 PSI 용어 질문 여부 판단
def is_valid_term_question(user_input: str) -> bool:
    prompt = f"""
    당신은 'PSI 시스템 용어 설명 에이전트'입니다.

    사용자 입력:
    "{user_input}"

    이 문장이 PSI 시스템 관련 용어(Max SR, Main SP, Allocation, SP, SR 등)에 대한 설명 요청이면 'YES'만 출력하세요.
    그렇지 않으면 'NO'만 출력하세요.
    """
    return ask_gpt(prompt).strip().upper().startswith("YES")

# ✅ 내부 청크 기반 용어 설명
def find_relevant_chunks(query: str, top_k: int = 1):
    from openai import Embedding

    embedding_response = Embedding.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = embedding_response["data"][0]["embedding"]

    def cosine_similarity(a, b):
        import numpy as np
        a, b = np.array(a), np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    # ✅ 사전 임베딩된 청크가 없기 때문에 유사도 측정 대신 키워드 기반 유사도 사용 (간이 방식)
    results = []
    for chunk in psi_chunks:
        text = chunk["text"]
        if any(k.lower() in text.lower() or k.lower() in query.lower() for k in chunk.get("keywords", [])):
            results.append((text, chunk["keywords"]))

    return results[:top_k] if results else []

# ✅ Term 에이전트 메인 함수
def explain_term(user_input: str):
    if not is_valid_term_question(user_input):
        return None

    matched_chunks = find_relevant_chunks(user_input)
    if matched_chunks:
        context = "\n---\n".join([c[0] for c in matched_chunks])
        prompt = f"""
        너는 PSI 시스템 매뉴얼 기반 설명 전문가야.

        아래는 관련 문서에서 검색된 내용입니다:
        {context}

        위 내용을 참고해서 사용자의 질문 '{user_input}'에 대해 정확하고 쉽게 설명해주세요.
        """
        return stream_chat_completion(prompt, user_input)

    # 🔁 fallback: GPT 자체 지식 기반 설명
    fallback_prompt = f"""
    사용자가 '{user_input}'라는 문장에서 어떤 용어에 대해 물어보고 있어.
    이 용어는 내부 매뉴얼에는 없지만, PSI 맥락에서 GPT가 유추하여 설명해줘.
    """
    return stream_chat_completion(fallback_prompt, user_input)

# ✅ supervisor_agent에서 import 할 수 있도록 alias 선언
term_agent = explain_term
