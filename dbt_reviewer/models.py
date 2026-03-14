from enum import Enum
from typing import Optional

from pydantic import BaseModel


class Source(str, Enum):
    CHECK = "check"
    LLM = "llm"


class Finding(BaseModel):
    file: str
    line: Optional[int] = None
    severity: str  # INFO | WARNING | ERROR
    message: str
    source: Source = Source.CHECK


class FindingsResponse(BaseModel):
    findings: list[Finding]
