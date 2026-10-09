"""Decision fusion strategies for Wardmote.

A merger takes the results of multiple detectors and produces a single
`Decision`. The choice of strategy determines how sensitive the pipeline is
to individual detector verdicts.
"""

from __future__ import annotations

from typing import Literal

from wardmote.types import Action, Decision, DetectorResult

Strategy = Literal["unanimous", "majority"]


class DecisionMerger:
    """Fuses detector results into a single Decision using a strategy.

    A merger never sees the content itself — only the verdicts. This keeps
    the fusion logic pure and testable independently of any detector.
    """

    def __init__(self, strategy: Strategy = "majority") -> None:
        if strategy not in ("unanimous", "majority"):
            raise ValueError(f"Unknown strategy: {strategy!r}")
        self._strategy: Strategy = strategy

    @property
    def strategy(self) -> Strategy:
        """The fusion strategy in use."""
        return self._strategy

    def merge(self, results: list[tuple[str, DetectorResult]]) -> Decision:
        """Combine named detector results into a single Decision.

        Each tuple is ``(detector_name, result)``. The merger uses the name
        only for the audit trail, never for the decision itself.
        """
        if not results:
            return Decision(action=Action.ALLOW)

        triggered = [(name, r) for name, r in results if r.triggered]
        total = len(results)

        if self._strategy == "unanimous":
            blocked = len(triggered) == total
        else:  # majority
            blocked = len(triggered) * 2 > total

        if not blocked:
            return Decision(action=Action.ALLOW)

        return Decision(
            action=Action.BLOCK,
            contributing_detectors=[name for name, _ in triggered],
            reason_chain=[r.reason for _, r in triggered if r.reason is not None],
        )
