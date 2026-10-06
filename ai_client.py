import os

import requests


API_URL = "https://copa.codyssey.kr/v1/messages"
API_KEY_ENV = "AI_API_KEY"
ANTHROPIC_VERSION = "2023-06-01"

DEFAULT_TIMEOUT = 30


class AIClientError(Exception):
    """AI API 호출 과정에서 발생한 오류."""


def get_api_key():
    """
    환경변수에서 AI API Key를 가져온다.
    """

    api_key = os.getenv(API_KEY_ENV)

    if not api_key:
        raise AIClientError(
            f"{API_KEY_ENV} 환경변수가 설정되지 않았습니다."
        )

    return api_key


def extract_text(data):
    """
    Anthropic Messages API 응답에서 텍스트를 추출한다.

    예상 응답:
    {
        "content": [
            {
                "type": "text",
                "text": "..."
            }
        ]
    }
    """

    try:
        content = data["content"]

        if not content:
            raise AIClientError(
                "AI 응답의 content가 비어 있습니다."
            )

        texts = []

        for item in content:
            if item.get("type") == "text":
                text = item.get("text")

                if text:
                    texts.append(text)

        if not texts:
            raise AIClientError(
                "AI 응답에서 텍스트를 찾을 수 없습니다."
            )

        return "\n".join(texts)

    except (KeyError, TypeError) as error:
        raise AIClientError(
            "AI 응답 형식이 예상과 다릅니다."
        ) from error


def request_ai(
    prompt,
    model,
    temperature,
    max_tokens,
):
    """
    Anthropic Messages API를 호출하고
    생성된 텍스트를 반환한다.
    """

    api_key = get_api_key()

    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": (
            "당신은 Git 변경 사항을 분석하는 "
            "소프트웨어 개발 도우미입니다."
        ),
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=DEFAULT_TIMEOUT,
        )

    except requests.exceptions.Timeout as error:
        raise AIClientError(
            "AI API 요청 시간이 초과되었습니다."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise AIClientError(
            "AI API 서버에 연결할 수 없습니다."
        ) from error

    except requests.exceptions.RequestException as error:
        raise AIClientError(
            f"AI API 요청 중 오류가 발생했습니다: {error}"
        ) from error

    # HTTP 상태 코드별 오류 처리
    if response.status_code == 401:
        raise AIClientError(
            "AI API 인증에 실패했습니다. API Key를 확인해주세요."
        )

    if response.status_code == 403:
        raise AIClientError(
            "AI API 접근 권한이 없습니다."
        )

    if response.status_code == 429:
        raise AIClientError(
            "AI API 요청 한도를 초과했습니다."
        )

    if response.status_code >= 500:
        raise AIClientError(
            f"AI API 서버 오류가 발생했습니다. "
            f"(HTTP {response.status_code})"
        )

    if not response.ok:
        try:
            error_body = response.json()
        except ValueError:
            error_body = response.text

        raise AIClientError(
            f"AI API 호출에 실패했습니다. "
            f"(HTTP {response.status_code}) "
            f"{error_body}"
        )

    try:
        data = response.json()

    except ValueError as error:
        raise AIClientError(
            "AI API 응답을 JSON으로 변환할 수 없습니다."
        ) from error

    return extract_text(data)