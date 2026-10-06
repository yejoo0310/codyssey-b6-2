import os
import requests


API_URL = "https://copa.codyssey.kr/v1/messages"


def main():
    api_key = os.getenv("AI_API_KEY")

    if not api_key:
        print("[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.")
        return

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    payload = {
        "model": "claude-haiku-4",
        "max_tokens": 200,
        "system": "당신은 간결하게 답변하는 개발 도우미입니다.",
        "messages": [
            {
                "role": "user",
                "content": "Python subprocess가 무엇인지 한 문장으로 설명해줘.",
            }
        ],
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    print("status code:", response.status_code)
    print(response.json())


if __name__ == "__main__":
    main()