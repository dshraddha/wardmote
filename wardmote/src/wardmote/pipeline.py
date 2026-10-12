"""The Wardmote pipeline — the core orchestrator."""

from __future__ import annotations

from wardmote.merger import DecisionMerger
from wardmote.protocols import Detector
from wardmote.types import (
    Action,
    Decision,
    DetectorContext,
    DetectorResult,
    Stage,
)


class Pipeline:
    """Orchestrates detectors and produces a single Decision per stage."""

    def __init__(self, merger: DecisionMerger | None = None) -> None:
        self._merger = merger or DecisionMerger()
        self._detectors: list[Detector] = []

    @property
    def detectors(self) -> tuple[Detector, ...]:
        """A read-only view of the registered detectors."""
        return tuple(self._detectors)

    def register(self, detector: object) -> None:
        """Add a detector to the pipeline.

        Accepts ``object`` so that callers from untyped code cannot bypass
        validation. The runtime check ensures the argument satisfies the
        ``Detector`` Protocol; the type checker enforces the same for
        typed callers.
        """
        if not isinstance(detector, Detector):
            raise TypeError(f"{type(detector).__name__} does not satisfy the Detector Protocol")
        self._detectors.append(detector)

    def run(
        self,
        content: str,
        stage: Stage,
        context: DetectorContext | None = None,
    ) -> Decision:
        """Run every detector registered for ``stage`` and merge the results."""
        ctx: DetectorContext = context or {}
        active = [d for d in self._detectors if stage in d.stages]

        if not active:
            return Decision(action=Action.ALLOW)

        results: list[tuple[str, DetectorResult]] = []
        errors: list[str] = []
        for detector in active:
            try:
                result = detector.detect(content, ctx)
            except Exception:
                errors.append(f"detector {detector.name!r} raised an exception")
                result = DetectorResult(triggered=False, confidence=0.0)
            results.append((detector.name, result))

        decision = self._merger.merge(results)
        if errors:
            decision = Decision(
                action=decision.action,
                contributing_detectors=decision.contributing_detectors,
                reason_chain=decision.reason_chain,
                errors=errors,
            )
        return decision
