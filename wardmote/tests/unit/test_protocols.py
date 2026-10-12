"""Tests for wardmote.protocols."""

from wardmote.protocols import Detector
from wardmote.types import DetectorContext, DetectorResult, Stage


class ValidDetector:
    """A class that satisfies the Detector Protocol without inheriting it."""

    name = "valid_detector"
    stages = frozenset({Stage.INPUT})

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        return DetectorResult(triggered=False, confidence=0.0)


class InvalidDetectorMissingDetect:
    """A class missing the `detect` method — should fail the Protocol check."""

    name = "invalid_missing_detect"
    stages = frozenset({Stage.INPUT})


def test_valid_detector_satisfies_protocol() -> None:
    detector = ValidDetector()
    assert isinstance(detector, Detector)


def test_invalid_detector_does_not_satisfy_protocol() -> None:
    detector = InvalidDetectorMissingDetect()
    assert not isinstance(detector, Detector)


def test_valid_detector_detect_returns_result() -> None:
    detector = ValidDetector()
    result = detector.detect("hello", {})
    assert result.triggered is False
    assert result.confidence == 0.0
