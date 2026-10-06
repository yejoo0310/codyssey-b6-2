ALLOWED_COMMIT_TYPES = {
    "feat",
    "fix",
    "docs",
    "refactor",
    "test",
    "chore",
}


def validate_commit_message(message):
    errors = []

    lines = [
        line.strip()
        for line in message.strip().splitlines()
        if line.strip()
    ]

    if len(lines) != 1:
        errors.append("커밋 메시지는 한 줄이어야 합니다.")
        return errors

    title = lines[0]

    if len(title) > 72:
        errors.append("커밋 제목이 72자를 초과했습니다.")

    if ":" not in title:
        errors.append("커밋 메시지 형식이 올바르지 않습니다.")
        return errors

    commit_type, subject = title.split(":", 1)

    commit_type = commit_type.strip()
    subject = subject.strip()

    if commit_type not in ALLOWED_COMMIT_TYPES:
        errors.append(
            f"허용되지 않은 커밋 타입입니다: {commit_type}"
        )

    if not subject:
        errors.append("커밋 제목 내용이 없습니다.")

    return errors