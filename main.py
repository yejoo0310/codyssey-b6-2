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

from prompts import build_commit_prompt

from validators import validate_commit_message


DEFAULT_MODEL = "claude-haiku-4"
DEFAULT_TEMPERATURE = 0.2
DEFAULT_MAX_TOKENS = 500


def parse_args():
    parser = argparse.ArgumentParser(
        description="AI 기반 Git 커밋/PR 자동 생성기"
    )

    parser.add_argument(
        "command",
        choices=["commit", "pr"],
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=DEFAULT_MAX_TOKENS,
    )

    parser.add_argument(
        "--safe-mode",
        action="store_true",
    )

    return parser.parse_args()


def validate_args(args):
    if not 0 <= args.temperature <= 1:
        raise ValueError(
            "temperature는 0 이상 1 이하로 입력해주세요."
        )

    if args.max_tokens <= 0:
        raise ValueError(
            "max-tokens는 1 이상의 정수여야 합니다."
        )


def main():
    args = parse_args()

    try:
        validate_args(args)

    except ValueError as error:
        print(f"[ERROR] {error}")
        return

    if not is_git_repository():
        print("[ERROR] Git 저장소가 아닙니다.")
        return

    try:
        status = get_git_status()

        if not status:
            print("[INFO] 변경 사항이 없습니다.")
            return

        diff = get_git_diff()

    except RuntimeError as error:
        print(
            f"[ERROR] Git 명령 실행 실패: {error}"
        )
        return

    changed_files = len(status.splitlines())
    diff_lines = len(diff.splitlines())

    print(
        f"[INFO] Git status 수집 완료: "
        f"{changed_files}개 파일 변경 감지"
    )

    print(
        f"[INFO] Git diff 수집 완료: "
        f"{diff_lines}줄"
    )

    if args.command == "commit":
        prompt = build_commit_prompt(
            status=status,
            diff=diff,
        )

    elif args.command == "pr":
        print(
            "[INFO] PR 생성 기능은 아직 구현되지 않았습니다."
        )
        return

    print("[INFO] AI API 요청 중...")

    try:
        result = request_ai(
            prompt=prompt,
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )

    except AIClientError as error:
        print(f"[ERROR] {error}")
        return

    errors = validate_commit_message(result)

    for error in errors:
        print(f"[WARNING] {error}")


    print("[INFO] API 호출 횟수: 1")
    print("[DONE] 커밋 메시지 생성 완료")

    print()
    print("--- Commit Message ---")
    print(result)
    print("----------------------")


if __name__ == "__main__":
    main()