import sqlglot

from dbt_reviewer.models import Finding


def check_select_star(sql: str, file: str):
    """
    Look for SELECT * in queries.
    We want to avoid this because:
    - It can break things if the source table changes
    - Usually pulls more data than needed
    - Makes it harder to understand what columns are actually being used
    """
    findings: list[Finding] = []

    try:
        tree = sqlglot.parse_one(sql)
    except sqlglot.errors.ParseError:
        return findings  # unparseable SQL (e.g. Jinja templates) — skip silently

    for select in tree.find_all(sqlglot.exp.Select):
        for projection in select.expressions:
            if projection.is_star:
                findings.append(
                    Finding(
                        file=file,
                        severity="WARNING",
                        message="SELECT * detected. Explicit columns recommended.",
                    )
                )

    return findings


def check_hardcoded_schema(sql: str, file: str):
    """
    Catch places where people hardcode database.schema.table instead of using ref().
    Hardcoded schemas cause problems when moving code between dev/test/prod.
    """
    findings = []

    tokens = sql.lower().split()

    for token in tokens:
        if "." in token and "ref(" not in token:
            if token.count(".") >= 2:
                findings.append(
                    Finding(
                        file=file,
                        severity="WARNING",
                        message="Hardcoded schema/table reference detected.",
                    )
                )
                break

    return findings


def check_many_joins(sql: str, file: str):
    """
    Flag queries with lots of joins - they can be slow and might indicate
    that the data model needs some work.
    """
    findings = []

    join_count = sql.lower().count(" join ")

    if join_count >= 3:
        findings.append(
            Finding(
                file=file,
                severity="INFO",
                message=f"Query has {join_count} joins. Possible performance or fanout risk.",
            )
        )

    return findings


def check_hardcoded_dates(sql: str, file: str):
    """
    Look for hardcoded dates in queries.
    Things like '2023-01-01' or DATE('2024-12-31') become stale over time.
    Better to use relative date logic like CURRENT_DATE or dateadd instead.
    """
    findings = []

    # Common patterns for hardcoded dates
    sql_upper = sql.upper()

    # Look for quoted dates
    if "'202" in sql or '"202' in sql:
        # If it's a BETWEEN clause, it's more likely to be a date filter
        if "BETWEEN" in sql_upper:
            findings.append(
                Finding(
                    file=file,
                    severity="WARNING",
                    message="Found hardcoded dates in BETWEEN clause. Consider using dynamic dates like CURRENT_DATE instead.",
                )
            )
        else:
            findings.append(
                Finding(
                    file=file,
                    severity="INFO",
                    message="Found what looks like a hardcoded date. Consider making it dynamic.",
                )
            )

    return findings


def run_all_checks(sql: str, file: str):
    """
    Run all the checks and collect the results.
    """
    findings = []
    findings += check_select_star(sql, file)
    findings += check_hardcoded_schema(sql, file)
    findings += check_many_joins(sql, file)
    findings += check_hardcoded_dates(sql, file)

    return findings
