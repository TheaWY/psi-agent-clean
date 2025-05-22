import chromadb
from chromadb.config import Settings

# Chroma DB 경로
CHROMA_DB_DIR = "./chroma"
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)

# 기존 컬렉션 불러오기
collection = client.get_or_create_collection(name="psi_chunks")

# 저장된 문서 수 확인
count = collection.count()
print(f"✅ 현재 저장된 문서 수: {count}")

# 일부 문서 미리보기
results = collection.get(include=["documents", "metadatas"], limit=5)
for i in range(len(results["ids"])):
    print(f"\n📌 ID: {results['ids'][i]}")
    print(f"📎 텍스트: {results['documents'][i][:100]}...")
    print(f"🏷️ 메타데이터: {results['metadatas'][i]}")
