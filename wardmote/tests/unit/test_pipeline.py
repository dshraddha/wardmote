"""Tests for wardmote.pipeline."""

import pytest

from wardmote.pipeline import Pipeline
from wardmote.types import (
    Action,
    DetectorContext,
    DetectorResult,
    Stage,
)


class AlwaysTriggers:
    name = "always"
    stages = frozenset({Stage.INPUT})

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        return DetectorResult(triggered=True, confidence=1.0, reason="always fires")


class NeverTriggers:
    name = "never"
    stages = frozenset({Stage.INPUT})

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        return DetectorResult(triggered=False, confidence=0.0)


class RaisesOnDetect:
    name = "raiser"
    stages = frozenset({Stage.INPUT})

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        raise RuntimeError("boom")


class OutputOnly:
    name = "output_only"
    stages = frozenset({Stage.OUTPUT})

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        return DetectorResult(triggered=True, confidence=1.0)


def test_empty_pipeline_allows() -> None:
    pipeline = Pipeline()
    assert pipeline.run("hi", stage=Stage.INPUT).action == Action.ALLOW


def test_no_detectors_for_stage_allows() -> None:
    pipeline = Pipeline()
    pipeline.register(OutputOnly())
    assert pipeline.run("hi", stage=Stage.INPUT).action == Action.ALLOW


def test_unanimous_block_when_all_trigger() -> None:
    pipeline = Pipeline()
    pipeline.register(AlwaysTriggers())
    pipeline.register(AlwaysTriggers())
    assert pipeline.run("hi", stage=Stage.INPUT).action == Action.BLOCK


def test_majority_allows_when_only_one_triggers() -> None:
    pipeline = Pipeline()
    pipeline.register(AlwaysTriggers())
    pipeline.register(NeverTriggers())
    pipeline.register(NeverTriggers())
    assert pipeline.run("hi", stage=Stage.INPUT).action == Action.ALLOW


def test_detector_exception_is_isolated() -> None:
    pipeline = Pipeline()
    pipeline.register(RaisesOnDetect())
    pipeline.register(AlwaysTriggers())
    pipeline.register(AlwaysTriggers())
    decision = pipeline.run("hi", stage=Stage.INPUT)
    # The raiser is treated as not triggered; the two AlwaysTriggers win majority.
    assert decision.action == Action.BLOCK
    assert "raiser" not in decision.contributing_detectors


def test_detector_exception_reason_recorded() -> None:
    pipeline = Pipeline()
    pipeline.register(RaisesOnDetect())
    pipeline.register(NeverTriggers())
    pipeline.register(NeverTriggers())
    decision = pipeline.run("hi", stage=Stage.INPUT)
    assert any("raised an exception" in e for e in decision.errors)


def test_register_rejects_non_detector() -> None:
    pipeline = Pipeline()

    class NotADetector:
        pass

    with pytest.raises(TypeError, match="does not satisfy the Detector Protocol"):
        pipeline.register(NotADetector())


def test_detectors_property_is_immutable_view() -> None:
    pipeline = Pipeline()
    pipeline.register(AlwaysTriggers())
    snapshot = pipeline.detectors
    assert isinstance(snapshot, tuple)
    assert len(snapshot) == 1
