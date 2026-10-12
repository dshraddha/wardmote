"""Wardmote — compose LLM security detectors into one pipeline."""

from wardmote.adapters.regex import RegexDetector
from wardmote.merger import DecisionMerger
from wardmote.pipeline import Pipeline
from wardmote.protocols import Detector
from wardmote.types import (
    Action,
    Decision,
    DetectorContext,
    DetectorResult,
    Stage,
)

__version__ = "0.0.1"

__all__ = [
    "Action",
    "Decision",
    "DecisionMerger",
    "Detector",
    "DetectorContext",
    "DetectorResult",
    "Pipeline",
    "RegexDetector",
    "Stage",
]
