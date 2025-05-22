# utils/chat_completion.py

import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def stream_chat_completion(system_prompt: str, user_input: str):
    """
    OpenAI GPT 모델을 system + user messages 구조로 스트리밍 방식 응답하는 함수
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        stream=True,
    )
    for chunk in response:
        if "choices" in chunk and len(chunk["choices"]) > 0:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]
