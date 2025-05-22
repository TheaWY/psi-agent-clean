# agents/tracking_agent.py

from utils.chat_completion import stream_chat_completion

def track_psi_component(user_input: str):
    """
    PSI 수치의 세부 구성 요소를 추적하고 설명합니다.
    예: 특정 제품의 재고, 생산, 수요가 PSI에 미친 영향 등.
    """
    prompt = f"""
    사용자가 PSI 구성요소를 추적하려고 합니다. 다음 질문에 대해 설명해 주세요:

    "{user_input}"

    💡 PSI 수치를 구성하는 요소(수요, 공급, 재고 등) 중 어떤 항목이 어떤 식으로 영향을 주었는지 추론하여,
    전문가처럼 설명해 주세요. 수치가 없더라도 plausible한 가정을 사용해 주세요.
    """
    return stream_chat_completion(prompt)
