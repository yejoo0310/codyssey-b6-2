import re


SENSITIVE_PATTERNS = [
    # 이메일
    (
        re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
        ),
        "[REDACTED_EMAIL]",
    ),

    # API Key / Secret / Token / Password
    (
        re.compile(
            r"(?i)"
            r"(api[_-]?key|secret|token|password)"
            r"\s*[:=]\s*"
            r"['\"]?"
            r"[A-Za-z0-9_\-./+=]{8,}"
            r"['\"]?"
        ),
        r"\1=[REDACTED_SECRET]",
    ),

    # Bearer Token
    (
        re.compile(
            r"(?i)Bearer\s+[A-Za-z0-9._\-]+"
        ),
        "Bearer [REDACTED_TOKEN]",
    ),
]


def mask_sensitive_data(text):
    """
    민감정보로 판단되는 문자열을 마스킹한다.

    반환값:
        (마스킹된 문자열, 마스킹 횟수)
    """

    masked_text = text
    total_count = 0

    for pattern, replacement in SENSITIVE_PATTERNS:
        masked_text, count = pattern.subn(
            replacement,
            masked_text,
        )

        total_count += count

    return masked_text, total_count


def apply_safe_mode(diff):
    """
    Safe mode 적용:
    민감정보만 마스킹한다.
    """

    masked_diff, masked_count = mask_sensitive_data(diff)

    return {
        "diff": masked_diff,
        "masked_count": masked_count,
    }