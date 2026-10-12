"""Regex-based detector for Wardmote.

The simplest possible Detector implementation: a set of named regular
expressions compiled once at construction time.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from wardmote.types import DetectorResult, Stage

if TYPE_CHECKING:
    from wardmote.types import DetectorContext


class RegexDetector:
    """Triggers when any of its named patterns matches the content.

    Patterns are compiled once at construction time. If any pattern is
    invalid, the constructor raises immediately rather than failing later
    at detection time.
    """

    name: str = "regex"
    stages: frozenset[Stage] = frozenset({Stage.INPUT, Stage.OUTPUT})

    def __init__(
        self,
        patterns: dict[str, str],
        *,
        flags: int = 0,
        name: str | None = None,
    ) -> None:
        if not patterns:
            raise ValueError("RegexDetector requires at least one pattern")

        self._patterns: list[tuple[str, re.Pattern[str]]] = []
        for pattern_name, raw in patterns.items():
            try:
                compiled = re.compile(raw, flags)
            except re.error as exc:
                raise ValueError(f"Invalid regex for pattern {pattern_name!r}: {exc}") from exc
            self._patterns.append((pattern_name, compiled))

        if name is not None:
            self.name = name

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        """Return a triggered result if any pattern matches."""
        matched = [n for n, p in self._patterns if p.search(content)]
        if not matched:
            return DetectorResult(triggered=False, confidence=1.0)
        return DetectorResult(
            triggered=True,
            confidence=1.0,
            reason="matched: " + ", ".join(matched),
        )
