from git_utils import (
    is_git_repository,
    get_git_status,
    get_git_diff,
)


def main():

    if not is_git_repository():
        print("[ERROR] Git 저장소가 아닙니다.")
        return


    try:
        status = get_git_status()

        if not status:
            print(
                "[INFO] 변경 사항이 없습니다."
            )
            return


        diff = get_git_diff()


        changed_files = len(
            status.splitlines()
        )

        diff_lines = len(
            diff.splitlines()
        )


        print(
            f"[INFO] Git status 수집 완료: "
            f"{changed_files}개 파일 변경 감지"
        )

        print(
            f"[INFO] Git diff 수집 완료: "
            f"{diff_lines}줄"
        )


        print()
        print("=== Git Status ===")
        print(status)

        print()
        print("=== Git Diff ===")
        print(diff)


    except RuntimeError as e:
        print(f"[ERROR] Git 명령 실행 실패: {e}")


if __name__ == "__main__":
    main()