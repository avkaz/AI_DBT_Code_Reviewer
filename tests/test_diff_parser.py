from dbt_reviewer.diff_parser import extract_sql_files


def test_extract_sql_files():
    diff = "+++ b/tests/sql/bad_orders.sql"
    files = extract_sql_files(diff)

    assert "tests/sql/bad_orders.sql" in files
