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
        errors.append(f"허용되지 않은 커밋 타입입니다: {commit_type}")

    if not subject:
        errors.append("커밋 제목 내용이 없습니다.")

    return errors


def sanitize_commit_message(message):
    lines = [
        line.strip()
        for line in message.strip().splitlines()
        if line.strip()
    ]

    if not lines:
        return "chore: 변경 사항 정리"

    title = lines[0]

    if ":" not in title:
        title = f"chore: {title}"

    commit_type, subject = title.split(":", 1)

    commit_type = commit_type.strip()
    subject = subject.strip()

    if commit_type not in ALLOWED_COMMIT_TYPES:
        commit_type = "chore"

    title = f"{commit_type}: {subject}"

    if len(title) > 72:
        title = title[:72].rstrip()

    return title


def validate_pr_title(title):
    errors = []

    if not title.strip():
        errors.append("PR 제목이 없습니다.")

    if "\n" in title.strip():
        errors.append("PR 제목은 한 줄이어야 합니다.")

    if len(title.strip()) > 80:
        errors.append("PR 제목이 80자를 초과했습니다.")

    return errors

def sanitize_pr_title(title):
    title = title.strip()

    if "\n" in title:
        title = title.splitlines()[0].strip()

    if len(title) > 80:
        title = title[:80].rstrip()

    return title

def validate_pr_body(body):
    errors = []

    sections = [
        "## Why",
        "## What",
        "## How to Test",
    ]

    for index, section in enumerate(sections):
        if section not in body:
            errors.append(f"PR 본문에 {section} 섹션이 없습니다.")
            continue

        start = body.find(section)

        if index + 1 < len(sections):
            next_section = sections[index + 1]

            end = body.find(
                next_section,
                start,
            )

            section_content = body[start + len(section):end]

        else:
            section_content = body[start + len(section):]

        bullet_exists = any(
            line.strip().startswith("- ")
            for line in section_content.splitlines()
        )

        if not bullet_exists:
            errors.append(f"{section} 섹션에 불릿이 없습니다.")

    return errors

def sanitize_pr_body(body):
    body = body.strip()

    body = body.replace(
        "## How\n",
        "## How to Test\n"
    )

    sections = [
        "## Why",
        "## What",
        "## How to Test",
    ]

    for index, section in enumerate(sections):
        if section not in body:
            body += (
                f"\n\n{section}\n"
                "- 내용 확인 필요"
            )

    lines = body.splitlines()

    result = []

    current_section = None
    section_has_bullet = {}

    for section in sections:
        section_has_bullet[section] = False

    for line in lines:
        stripped = line.strip()

        if stripped in sections:
            current_section = stripped
            result.append(line)
            continue

        if (
            current_section
            and stripped.startswith("- ")
        ):
            section_has_bullet[
                current_section
            ] = True

        result.append(line)

    final_result = []

    current_section = None

    for line in result:
        stripped = line.strip()

        if stripped in sections:
            if (
                current_section
                and not section_has_bullet[
                    current_section
                ]
            ):
                final_result.append(
                    "- 내용 확인 필요"
                )

            current_section = stripped

        final_result.append(line)

    if (
        current_section
        and not section_has_bullet[
            current_section
        ]
    ):
        final_result.append(
            "- 내용 확인 필요"
        )

    return "\n".join(
        final_result
    )