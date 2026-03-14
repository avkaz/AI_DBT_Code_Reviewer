from dbt_reviewer.checks import run_all_checks
from dbt_reviewer.diff_parser import extract_sql_files
from dbt_reviewer.llm_review import semantic_review
from dbt_reviewer.models import Finding


def _infer_context(file: str) -> dict:
    """Build context from filename"""
    parts = file.replace("\\", "/").split("/")
    model_name = parts[-1].replace(".sql", "")

    model_type = "unknown"
    for part in parts:
        if part in ("staging", "stg"):
            model_type = "staging"
        elif part in ("marts", "mart"):
            model_type = "mart"
        elif part in ("intermediate", "int"):
            model_type = "intermediate"

    return {"model_name": model_name, "model_type": model_type}


def run_review(diff_text: str):
    findings: list[Finding] = []

    files = extract_sql_files(diff_text)

    for file in files:
        try:
            with open(file, "r") as f:
                sql = f.read()
        except Exception:
            findings.append(
                Finding(
                    file=file,
                    severity="ERROR",
                    message="Failed to read SQL file.",
                )
            )
            continue
        context = _infer_context(file)
        findings += run_all_checks(sql, file)
        findings += semantic_review(sql, file, context=context)

    return findings
