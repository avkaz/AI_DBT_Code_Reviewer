import argparse
import sys

from dbt_reviewer.formatter import print_report
from dbt_reviewer.reviewer import run_review


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("diff_file", help="Path to git diff file")

    args = parser.parse_args()

    with open(args.diff_file) as f:
        diff_text = f.read()

    findings = run_review(diff_text)

    print_report(findings)

    if any(f.severity == "ERROR" for f in findings):
        sys.exit(1)


if __name__ == "__main__":
    main()
