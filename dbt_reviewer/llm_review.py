import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from openai import OpenAI, OpenAIError
from pydantic import ValidationError

from dbt_reviewer.llm_check_config import LLM_CHECKS, LLM_SKIP_CHECKS
from dbt_reviewer.models import Finding, FindingsResponse, Source

load_dotenv()

logger = logging.getLogger(__name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

PROMPTS_DIR = Path(__file__).parent / "prompts"
_jinja_env = Environment(loader=FileSystemLoader(PROMPTS_DIR), autoescape=True)

SYSTEM_PROMPT = (PROMPTS_DIR / "system.txt").read_text().strip()


def _build_user_prompt(sql: str, context: Optional[dict] = None) -> str:
    template = _jinja_env.get_template("semantic_review.j2")
    return template.render(
        sql=sql,
        context=context,
        checks=LLM_CHECKS,
        skip_checks=LLM_SKIP_CHECKS,
    )


def semantic_review(
    sql: str,
    file: str,
    context: Optional[dict] = None,
) -> list[Finding]:
    prompt = _build_user_prompt(sql, context)

    try:
        response = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            temperature=0,
            max_tokens=1024,
            response_format=FindingsResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        result = response.choices[0].message.parsed
        if result is None:
            logger.warning("LLM returned no parsed result for %s", file)
            return [
                Finding(
                    file=file,
                    severity="INFO",
                    message="LLM semantic check could not run.",
                )
            ]

        for finding in result.findings:
            finding.file = file
            finding.source = Source.LLM
        return result.findings

    except (ValidationError, OpenAIError) as exc:
        logger.error("Semantic review failed for %s: %s", file, exc)
        return [
            Finding(
                file=file, severity="INFO", message="LLM semantic check could not run."
            )
        ]
