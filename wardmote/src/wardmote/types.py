"""Core type definitions for Wardmote."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TypedDict


class Stage(Enum):
    """The stage of an LLM interaction where a detector runs."""

    INPUT = "input"
    OUTPUT = "output"


class Action(Enum):
    """The decision the pipeline makes after running detectors."""

    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"
    FLAG = "flag"


@dataclass(frozen=True)
class DetectorResult:
    """The result returned by a single detector."""

    triggered: bool
    confidence: float
    reason: str | None = None


@dataclass(frozen=True)
class Decision:
    """The final decision produced by the pipeline."""

    action: Action
    contributing_detectors: list[str] = field(default_factory=list[str])
    reason_chain: list[str] = field(default_factory=list[str])


@dataclass(frozen=True)
class DetectorContext(TypedDict, total=False):
    """Optional context passed to detectors during detection.

    All fields are optional. Detectors must not assume any field is present.
    """

    user_id: str
    session_id: str
    conversation_history: tuple[str, ...]
    metadata: dict[str, str]
