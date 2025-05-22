import os, json, time
import openai, chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ChromaDB 초기화
client = chromadb.PersistentClient(path="./chroma")
collection = client.get_or_create_collection("psi_chunks")

# 수동 인사이트 로드
with open("./data/rag_chunks/psi_manual_insights.json", "r", encoding="utf-8") as f:
    manual_chunks = json.load(f)

# 기존 ID 조회 (peek 사용)
peeked = collection.peek(limit=10000)
existing_ids = set(peeked.get("ids", []))
print(f"📦 이미 존재하는 문서 수: {len(existing_ids)}개")

added_count = 0
for chunk in tqdm(manual_chunks, desc="➕ 새 문서 추가 중"):
    if chunk["id"] in existing_ids:
        continue

    try:
        # ⚠️ 3072차원 모델 사용
        emb = openai.Embedding.create(
            model="text-embedding-3-large",
            input=chunk["text"]
        )["data"][0]["embedding"]

        collection.add(
            ids=[chunk["id"]],
            documents=[chunk["text"]],
            metadatas=[{
                "source": "manual_insight",
                "keywords": ", ".join(chunk.get("keywords", []))
            }],
            embeddings=[emb]
        )
        added_count += 1
        print(f"✅ 추가 성공: {chunk['id']}")
    except Exception as e:
        print(f"❌ 실패: {chunk['id']} / {e}")
        time.sleep(1)

print(f"\n✅ 새로 추가된 문서 수: {added_count}개")
