# utils/analyze_rag_results.py

import json

RESULT_PATH = "./data/rag_test_results.json"

with open(RESULT_PATH, "r", encoding="utf-8") as f:
    results = json.load(f)

# ✅ 기본 통계
total = len(results)
confident = sum(1 for r in results if r["is_confident"])
avg_score = sum(r["score"] for r in results) / total if total else 0

print("📊 RAG 테스트 텍스트 분석 결과")
print(f"총 질문 수: {total}")
print(f"신뢰도 높은 응답 수: {confident} ({(confident / total * 100):.1f}%)")
print(f"평균 유사도 점수: {avg_score:.3f}\n")

# ✅ 낮은 유사도 문서만 하이라이트
print("❗ 유사도 낮은 응답 샘플 (상위 5개):")
low_conf = sorted(results, key=lambda x: x["score"])[:5]
for r in low_conf:
    print(f"\n❓ 질문: {r['question']}")
    print(f"   🔹 유사도 점수: {r['score']:.3f}")
    print(f"   🔹 신뢰도 판단: {'✅' if r['is_confident'] else '❌'}")
    print(f"   🔹 발췌 문서: {r['doc_snippet']}")
