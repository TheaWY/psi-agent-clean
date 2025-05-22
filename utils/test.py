# utils/test_inspect_chroma.py
import chromadb
from chromadb.config import Settings

CHROMA_DB_DIR = "./chroma"
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = client.get_or_create_collection(name="psi_chunks")

count = collection.count()
print(f"✅ 총 저장된 문서 수: {count}")

results = collection.get(include=["documents", "metadatas"], limit=5)
for i, doc in enumerate(results["documents"]):
    print(f"\n📄 문서 {i+1}:")
    print(f"텍스트: {doc[:100]}...")
    print(f"메타데이터: {results['metadatas'][i]}")
