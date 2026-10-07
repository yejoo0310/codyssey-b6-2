class ParseError(Exception):
    """AI 생성 결과 파싱 실패."""


def parse_pr_response(response):
    title_marker = "[PR_TITLE]"
    body_marker = "[PR_BODY]"

    if title_marker not in response:
        raise ParseError(
            "PR 응답에서 [PR_TITLE]을 찾을 수 없습니다."
        )

    if body_marker not in response:
        raise ParseError(
            "PR 응답에서 [PR_BODY]를 찾을 수 없습니다."
        )

    title_part, body = response.split(
        body_marker,
        1,
    )

    title = title_part.replace(
        title_marker,
        "",
        1,
    ).strip()

    body = body.strip()

    if not title:
        raise ParseError(
            "PR 제목이 비어 있습니다."
        )

    if not body:
        raise ParseError(
            "PR 본문이 비어 있습니다."
        )

    return title, body