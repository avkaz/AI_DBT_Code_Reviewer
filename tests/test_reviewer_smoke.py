from dbt_reviewer.reviewer import run_review


def test_smoke_review():
    diff = "+++ b/tests/sql/bad_orders.sql"

    findings = run_review(diff)

    assert len(findings) > 0
