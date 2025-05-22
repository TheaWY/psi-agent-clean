# utils/test_rag_batch.py
import os, json
from rag_query_handler import query_rag_with_score

questions = [
    "BOD를 연결하지 않으면 공급 계획은 어떻게 되나요?",
    "Frozen Period란 무엇인가요?",
    "Transit Time은 어떤 의미인가요?",
    "Site와 Item을 Assign한 뒤 해야 할 일은 무엇인가요?",
    "GSCP와 PSI는 어떤 관계인가요?",
    "PSI에서 Forecast와 Plan의 차이는 무엇인가요?",
    "Sales PSI, Shipment PSI, Production PSI는 각각 어떤 역할인가요?",
    "Item과 Site를 연결하기 위해 어떤 정보가 필요한가요?",
    "왜 BOD 연결이 PSI 계획 생성에 중요할까요?",
    "GSCP에서 Planning Data와 Dynamic Data는 어떤 차이가 있나요?",
]

os.makedirs("data", exist_ok=True)
with open("data/generated_rag_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, ensure_ascii=False, indent=2)

results = []
for q in questions:
    result = query_rag_with_score(q)
    results.append({
        "question": q,
        "score": result["score"],
        "is_confident": result["is_confident"],
        "doc_snippet": result["docs"][0][:100] if result["docs"] else "",
    })

with open("data/rag_test_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
