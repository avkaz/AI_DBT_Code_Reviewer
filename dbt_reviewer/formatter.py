from dbt_reviewer.models import Finding, Source


def _print_section(title: str, findings: list[Finding]) -> None:
    print(f"\n{'─' * 40}")
    print(f" {title}")
    print(f"{'─' * 40}")

    if not findings:
        print("No issues found.")
        return

    current_file = None
    for f in findings:
        if f.file != current_file:
            print(f"\n  FILE: {f.file}")
            current_file = f.file
        line = f" line {f.line}" if f.line else ""
        print(f"  [{f.severity}]{line} — {f.message}")


def print_report(findings: list[Finding]) -> None:
    checks = [f for f in findings if f.source == Source.CHECK]
    llm = [f for f in findings if f.source == Source.LLM]

    _print_section("Static checks", checks)
    _print_section("LLM semantic review", llm)
