# AI dbt Code Reviewer

**Note up front**
- I did not use the recommended repo as a starting point because I realized the task has the second page too late.
- I did not dockerize the solution because I felt a little bit lazy and wanted to deliver the core functionality fast.
- I use OpenAI API here because I had some tokens and did not want to organize something else, although OpenAI is a perfect fit for me.
- Any frameworks like LangChain would be overkill for this task as for me.

## Project structure

- `main.py` - entry point: parse diff path, run review, print report, exit non-zero on configured severities.
- `dbt_reviewer/diff_parser.py` - parse git diff content and return changed SQL file paths.
- `dbt_reviewer/checks.py` - static checks over SQL content.
- `dbt_reviewer/llm_review.py` - semantic review with OpenAI API, handles prompting and mapping to findings.
- `dbt_reviewer/reviewer.py` - orchestrates reading files, context, checks, and semantic review.
- `dbt_reviewer/formatter.py` - prints findings in human-readable format.
- `dbt_reviewer/models.py` - dataclasses and pydantic models for Findings and response shapes.
- `dbt_reviewer/llm_check_config.py` - check definitions and skip lists for LLM review.
- `tests/` - unit tests and sample diffs.

## How everything is connected

1. **`main.py`** reads diff path from `argv` and calls `run_review()`.
2. **`run_review`** uses `extract_sql_files()` to resolve changed SQL file paths.
3. For each file, it runs:
   - `run_all_checks(sql, file)` for local static checks.
   - `semantic_review(sql, file, context)` for LLM-based checks.
4. **`semantic_review`** uses OpenAI via `openai.OpenAI` and the prompt templates in `dbt_reviewer/prompts/`.
5. Findings are aggregated and formatted by `print_report()`.

## GitHub Actions pipeline trigger

- The repository includes `.github/workflows/dbt_review.yml` to run a pipeline when a PR is created.
- Pipeline checks whether any SQL files changed under `models/` and runs the same review flow.
- If checks fail, the PR shows failure status and a link for details (user can click to see failure reasons).

## Run locally

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run tests:

```bash
pytest -q
```

3. Run on diff files:

```bash
python main.py tests/diffs/diff_bad_orders.txt
python main.py tests/diffs/diff_suspicious.txt
```


## Future extensions & improvements

- Better context from SQL models:
  - current context is only file name + path-based type inference.
  - could include data model schema, upstream/downstream lineage, column metadata.
- dockerization (if desired) for consistent containers and CI.
- better config for `loguru` and verbosity.
- add retries/throttling around OpenAI API calls.
- add more LLM check rules and external rule sets.
