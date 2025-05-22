# agents/query_agent.py

from utils.chat_completion import stream_chat_completion

def query_database(user_input: str):
    """
    PSI 관련 데이터베이스 조회 요청을 처리합니다.
    예: 특정 항목의 수요, 재고, 납기 등
    """
    prompt = f"""
    사용자의 요청은 다음과 같습니다:
    "{user_input}"
    
    이 요청에 맞는 PSI 시스템 내의 정보를 데이터베이스에서 조회한 것처럼 요약해 주세요.
    실제 값은 없지만, plausible한 값으로 예시를 들어 정리해 주세요.
    """

    return stream_chat_completion(prompt)
