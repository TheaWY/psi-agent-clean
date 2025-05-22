import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# ✅ 기본 GPT 응답
def ask_gpt(prompt: str, model="gpt-4", temperature=0.3):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


# ✅ 스트리밍 응답: 감시 포함 (회피성 응답 감지 시 fallback으로 전환)
def stream_gpt_response(prompt: str, model="gpt-4", temperature=0.3, fallback_msg="❗ 관련 정보를 문서에서 찾을 수 없습니다. 추가 자료가 필요합니다."):
    """
    GPT 응답을 스트리밍하며 회피성 메시지를 감지하면 fallback 메시지로 대체합니다.
    """
    try:
        stream = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            stream=True,
        )

        buffer = ""
        for chunk in stream:
            if "choices" in chunk and len(chunk["choices"]) > 0:
                delta = chunk["choices"][0]["delta"]
                if "content" in delta:
                    content = delta["content"]
                    buffer += content

                    # 회피성 응답 패턴 감지
                    if any(key in buffer for key in [
                        "정확한 정보를 제공하기 어렵습니다",
                        "문서에 정보가 없습니다",
                        "제공된 문서에서 찾을 수 없습니다",
                        "잘 모르겠습니다",
                        "답변하기 어렵습니다",
                        "추측에 불과합니다"
                    ]):
                        yield fallback_msg
                        return

                    yield content
    except Exception as e:
        yield f"⚠️ GPT 호출 실패: {e}"
