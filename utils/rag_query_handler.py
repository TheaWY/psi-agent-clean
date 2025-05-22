# utils/rag_query_handler.py

import os
import sqlite3
import openai

# --- 1) OpenAI API 키 세팅 ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- 2) 문서 조회 (RAG) ---
def query_docs(query: str, top_k: int = 5):
    conn = sqlite3.connect("data/chroma.sqlite3")
    cur = conn.cursor()
    # 예시 테이블, 실제 스키마에 맞게 수정하세요
    cur.execute("SELECT doc, score FROM embeddings WHERE query = ? ORDER BY score DESC LIMIT ?", (query, top_k))
    results = cur.fetchall()
    docs = [r[0] for r in results]
    confidence = results[0][1] if results else 0.0
    conn.close()
    return docs, confidence

# --- 3) OpenAI 호출 래퍼 ---
def openai_completion(prompt: str) -> str:
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": prompt}
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content
