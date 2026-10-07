import argparse

from ai_client import (
    AIClientError,
    request_ai,
)

from git_utils import (
    get_git_diff,
    get_git_status,
    is_git_repository,
)

from parsers import (
    ParseError,
    parse_pr_response,
)

from prompts import (
    build_commit_prompt,
    build_pr_prompt,
)

from safety import apply_safe_mode

from validators import (
    sanitize_commit_message,
    sanitize_pr_body,
    sanitize_pr_title,
    validate_commit_message,
    validate_pr_body,
    validate_pr_title,
)


DEFAULT_MODEL = "claude-haiku-4"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 800


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI 기반 Git 커밋/PR 자동 생성기"
)

    parser.add_argument(
        "command",
        choices=["commit", "pr"],
        help="commit 메시지 또는 PR 초안 생성",
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=(f"사용할 AI 모델 (기본값: {DEFAULT_MODEL})"),
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=(f"AI 생성 temperature (기본값: {DEFAULT_TEMPERATURE})"),
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
        help=(f"최대 생성 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})"),
    )

    parser.add_argument(
        "--safe-mode",
        action="store_true",
        help="민감정보 마스킹 모드",
    )

    return parser.parse_args()


def validate_args(args):
    if not 0 <= args.temperature <= 1:
        raise ValueError("temperature는 0 이상 1 이하로 입력해주세요.")

    if args.max_tokens <= 0:
        raise ValueError("max-tokens는 1 이상의 정수여야 합니다.")


def collect_git_data():
    if not is_git_repository():
        raise RuntimeError("Git 저장소가 아닙니다.")

    status = get_git_status()

    if not status:
        return None, None

    diff = get_git_diff()

    return status, diff


def apply_safe_mode_if_needed(
    diff,
    safe_mode,
):
    if not safe_mode:
        return diff

    safe_result = apply_safe_mode(diff)

    print("[INFO] Safe mode 적용")
    print(f"[INFO] 민감정보 마스킹: {safe_result['masked_count']}건")

    return safe_result["diff"]


def build_prompt(
    command,
    status,
    diff,
):
    if command == "commit":
        return build_commit_prompt(
            status=status,
            diff=diff,
        )

    if command == "pr":
        return build_pr_prompt(
            status=status,
            diff=diff,
        )

    raise ValueError(f"지원하지 않는 command입니다: {command}")


def generate_ai_result(
    prompt,
    args,
):
    print("[INFO] AI API 요청 중...")

    result = request_ai(
        prompt=prompt,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )

    print("[INFO] API 호출 횟수: 1")

    return result


def handle_commit_result(result):
    errors = validate_commit_message(result)

    if errors:
        for error in errors:
            print(f"[WARNING] {error}")

        print("[INFO] 커밋 메시지를 후처리합니다.")

        result = sanitize_commit_message(result)

    final_errors = validate_commit_message(result)

    if final_errors:
        for error in final_errors:
            print(f"[WARNING] 후처리 후에도 오류가 있습니다: {error}")

    print("[DONE] 커밋 메시지 생성 완료")

    print()
    print("--- Commit Message ---")
    print(result.strip())
    print("----------------------")


def handle_pr_result(result):
    try:
        pr_title, pr_body = (parse_pr_response(result))

    except ParseError as error:
        print(f"[ERROR] PR 응답 파싱 실패: {error}")
        return

    title_errors = validate_pr_title(pr_title)

    body_errors = validate_pr_body(pr_body)

    errors = (title_errors + body_errors)

    if errors:
        for error in errors:
            print(f"[WARNING] {error}")

        print("[INFO] PR 초안을 후처리합니다.")

        pr_title = sanitize_pr_title(pr_title)

        pr_body = sanitize_pr_body(pr_body)

    final_errors = (
        validate_pr_title(pr_title)
        + validate_pr_body(pr_body)
    )

    if final_errors:
        for error in final_errors:
            print(f"[WARNING] 후처리 후에도 오류가 있습니다: {error}")

    print("[DONE] PR 초안 생성 완료")

    print()
    print("--- PR Title ---")
    print(pr_title)

    print()
    print("--- PR Body ---")
    print(pr_body)

    print("----------------------")


def main():
    args = parse_args()

    try:
        validate_args(args)

    except ValueError as error:
        print(f"[ERROR] {error}")
        return

    try:
        status, diff = collect_git_data()

    except RuntimeError as error:
        print(f"[ERROR] {error}")
        return

    if not status:
        print("[INFO] 변경 사항이 없습니다.")
        return

    changed_files = len(status.splitlines())

    diff_lines = len(diff.splitlines())

    print(f"[INFO] Git status 수집 완료: {changed_files}개 파일 변경 감지")

    print(f"[INFO] Git diff 수집 완료: {diff_lines}줄")

    diff = apply_safe_mode_if_needed(
        diff=diff,
        safe_mode=args.safe_mode,
    )
    
    print(f"[INFO] model: {args.model}")
    print(f"[INFO] temperature: {args.temperature}")
    print(f"[INFO] max_tokens: {args.max_tokens}")

    try:
        prompt = build_prompt(
            command=args.command,
            status=status,
            diff=diff,
        )

    except ValueError as error:
        print(f"[ERROR] {error}")
        return

    try:
        result = generate_ai_result(
            prompt=prompt,
            args=args,
        )

    except AIClientError as error:
        print(f"[ERROR] {error}")
        return

    if args.command == "commit":
        handle_commit_result(result)

    elif args.command == "pr":
        handle_pr_result(result)


if __name__ == "__main__":
    main()