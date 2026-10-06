import subprocess


def run_git_command(args):
    result = subprocess.run(
        ["git", *args],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def is_git_repository():
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )

    return result.returncode == 0


def get_git_status():
    return run_git_command(
        ["status", "--short"]
    )


def get_git_diff():
    unstaged_diff = run_git_command(
        ["diff"]
    )

    staged_diff = run_git_command(
        ["diff", "--cached"]
    )

    diffs = []

    if staged_diff:
        diffs.append(
            "=== Staged Changes ===\n"
            + staged_diff
        )

    if unstaged_diff:
        diffs.append(
            "=== Unstaged Changes ===\n"
            + unstaged_diff
        )

    return "\n\n".join(diffs)