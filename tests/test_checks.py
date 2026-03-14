from dbt_reviewer.checks import (
    check_hardcoded_dates,
    check_hardcoded_schema,
    check_many_joins,
    check_select_star,
    run_all_checks,
)

# ── check_select_star ──────────────────────────────────────────────────────────


def test_select_star_detected():
    findings = check_select_star("SELECT * FROM table1", "file.sql")
    assert any("SELECT *" in f.message for f in findings)


def test_select_star_not_triggered_on_explicit_columns():
    findings = check_select_star("SELECT id, name FROM table1", "file.sql")
    assert findings == []


# ── check_hardcoded_schema ─────────────────────────────────────────────────────


def test_hardcoded_schema_detected():
    findings = check_hardcoded_schema("SELECT * FROM db.schema.table", "file.sql")
    assert any("Hardcoded" in f.message for f in findings)


def test_hardcoded_schema_not_triggered_on_ref():
    findings = check_hardcoded_schema("SELECT * FROM {{ ref('my_model') }}", "file.sql")
    assert findings == []


def test_hardcoded_schema_not_triggered_on_single_dot():
    findings = check_hardcoded_schema("SELECT t.id FROM my_table t", "file.sql")
    assert findings == []


# ── check_many_joins ───────────────────────────────────────────────────────────


def test_many_joins_detected():
    sql = """
    SELECT a FROM t1
    JOIN t2 ON 1=1
    JOIN t3 ON 1=1
    JOIN t4 ON 1=1
    """
    findings = check_many_joins(sql, "file.sql")
    assert any("joins" in f.message for f in findings)


def test_few_joins_not_triggered():
    sql = "SELECT a FROM t1 JOIN t2 ON t1.id = t2.id"
    findings = check_many_joins(sql, "file.sql")
    assert findings == []


def test_many_joins_count_in_message():
    sql = "SELECT a FROM t1 JOIN t2 ON 1=1 JOIN t3 ON 1=1 JOIN t4 ON 1=1"
    findings = check_many_joins(sql, "file.sql")
    assert any("3" in f.message for f in findings)


# ── check_hardcoded_dates ──────────────────────────────────────────────────────


def test_hardcoded_date_in_between_detected():
    sql = "SELECT * FROM t WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'"
    findings = check_hardcoded_dates(sql, "file.sql")
    assert any("BETWEEN" in f.message for f in findings)
    assert findings[0].severity == "WARNING"


def test_hardcoded_date_outside_between_detected():
    sql = "SELECT * FROM t WHERE created_at > '2024-01-01'"
    findings = check_hardcoded_dates(sql, "file.sql")
    assert findings != []
    assert findings[0].severity == "INFO"


def test_no_hardcoded_date_not_triggered():
    findings = check_hardcoded_dates(
        "SELECT * FROM t WHERE created_at > CURRENT_DATE", "file.sql"
    )
    assert findings == []


# ── run_all_checks ─────────────────────────────────────────────────────────────


def test_run_all_checks_returns_findings():
    sql = "SELECT * FROM db.schema.table JOIN t2 ON 1=1 JOIN t3 ON 1=1 JOIN t4 ON 1=1"
    findings = run_all_checks(sql, "file.sql")
    assert len(findings) > 0


def test_run_all_checks_clean_sql():
    sql = "SELECT id, name FROM {{ ref('my_model') }}"
    findings = run_all_checks(sql, "file.sql")
    assert findings == []
