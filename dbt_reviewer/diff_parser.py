def extract_sql_files(diff_text: str) -> list[str]:
    """
    Extract changed SQL file paths from git diff.
    """
    files = []

    for line in diff_text.splitlines():
        if line.startswith("+++ b/") and line.endswith(".sql"):
            path = line.replace("+++ b/", "").strip()
            files.append(path)

    return list(set(files))
