import argparse
import sys

from dbt_reviewer.formatter import print_report
from dbt_reviewer.reviewer import run_review

BLOCKING_SEVERITIES = {"ERROR", "WARNING"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("diff_file", help="Path to git diff file")
    parser.add_argument(
        "--fail-on",
        nargs="+",
        default=list(BLOCKING_SEVERITIES),
        metavar="SEVERITY",
        help="Severities that cause a non-zero exit (default: ERROR WARNING)",
    )

    args = parser.parse_args()

    with open(args.diff_file) as f:
        diff_text = f.read()

    findings = run_review(diff_text)
    print_report(findings)

    blocking = {s.upper() for s in args.fail_on}
    if any(f.severity.upper() in blocking for f in findings):
        print("\nFailed: blocking findings detected.")
        sys.exit(1)


if __name__ == "__main__":
    main()
