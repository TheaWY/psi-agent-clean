# chroma_manager.py

import os
import json
import time
import openai
import chromadb
from tqdm import tqdm
from chromadb.config import Settings
from dotenv import load_dotenv

# ✅ 1. 환경 변수 로드 및 API 설정
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 2. 파일 경로 설정
DATA_PATH = "./data/rag_chunks/psi_slide_chunks.json"
CHROMA_DB_DIR = "./chroma"

# ✅ 3. Chroma 클라이언트 초기화
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

# ✅ 4. 기존 컬렉션 삭제 후 재생성
try:
    client.delete_collection("psi_chunks")
except:
    pass
collection = client.create_collection(name="psi_chunks")
print("✅ 컬렉션 재생성 완료")

# ✅ 5. JSON 데이터 로드
with open(DATA_PATH, "r", encoding="utf-8") as f:
    slide_data = json.load(f)
print(f"📄 총 문서 수: {len(slide_data)}")

# ✅ 6. 청크별 임베딩 생성 및 저장
for chunk in tqdm(slide_data, desc="📌 임베딩 중"):
    text = chunk["text"]
    chunk_id = chunk["id"]

    success = False
    for attempt in range(3):  # 최대 3회 재시도
        try:
            response = openai.Embedding.create(
                model="text-embedding-3-large",
                input=text,
                timeout=20  # 타임아웃 제한 (초)
            )
            embedding = response["data"][0]["embedding"]
            collection.add(
                ids=[chunk_id],
                documents=[text],
                metadatas=[{
                    "slide": chunk.get("slide_index"),
                    "source": chunk.get("source"),
                    "keywords": ", ".join(chunk.get("keywords", []))
                }],
                embeddings=[embedding]
            )
            success = True
            break
        except Exception as e:
            print(f"⏳ {chunk_id} 임베딩 실패 (시도 {attempt + 1}/3): {e}")
            time.sleep(2)  # 재시도 전 대기 시간

    if not success:
        print(f"❌ {chunk_id} 완전 실패 → 건너뜀")

print("✅ 모든 문서 임베딩 및 저장 완료.")
