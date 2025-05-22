import os
import json

# ✅ 질문 리스트
DEFAULT_QUESTIONS = [
    "BOD를 연결하지 않으면 공급 계획은 어떻게 되나요?",
    "Frozen Period란 무엇인가요?",
    "Transit Time은 어떤 의미인가요?",
    "Site와 Item을 Assign한 뒤 해야 할 일은 무엇인가요?",
    "GSCP와 PSI는 어떤 관계인가요?",
    "PSI에서 Forecast와 Plan의 차이는 무엇인가요?",
    "Sales PSI, Shipment PSI, Production PSI는 각각 어떤 역할인가요?",
    "Item과 Site를 연결하기 위해 어떤 정보가 필요한가요?",
    "왜 BOD 연결이 PSI 계획 생성에 중요할까요?",
    "GSCP에서 Planning Data와 Dynamic Data는 어떤 차이가 있나요?"
]

# ✅ 경로: 현재 디렉토리 하위로 설정
questions_path = "./data/generated_rag_questions.json"
os.makedirs(os.path.dirname(questions_path), exist_ok=True)

# ✅ 파일 생성 또는 확인
if not os.path.exists(questions_path):
    with open(questions_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_QUESTIONS, f, ensure_ascii=False, indent=2)
    print(f"📄 질문 파일 생성 완료: {questions_path}")
else:
    print(f"📂 기존 질문 파일 사용 중: {questions_path}")
