"""Tests for wardmote.merger."""

import pytest

from wardmote.merger import DecisionMerger
from wardmote.types import Action, DetectorResult


def _result(triggered: bool, reason: str | None = None) -> DetectorResult:
    return DetectorResult(triggered=triggered, confidence=0.9, reason=reason)


class TestUnanimous:
    def test_empty_input_allows(self) -> None:
        merger = DecisionMerger(strategy="unanimous")
        assert merger.merge([]).action == Action.ALLOW

    def test_all_triggered_blocks(self) -> None:
        merger = DecisionMerger(strategy="unanimous")
        results = [("a", _result(True)), ("b", _result(True))]
        assert merger.merge(results).action == Action.BLOCK

    def test_one_not_triggered_allows(self) -> None:
        merger = DecisionMerger(strategy="unanimous")
        results = [("a", _result(True)), ("b", _result(False))]
        assert merger.merge(results).action == Action.ALLOW


class TestMajority:
    def test_two_of_three_blocks(self) -> None:
        merger = DecisionMerger(strategy="majority")
        results = [
            ("a", _result(True)),
            ("b", _result(True)),
            ("c", _result(False)),
        ]
        assert merger.merge(results).action == Action.BLOCK

    def test_one_of_three_allows(self) -> None:
        merger = DecisionMerger(strategy="majority")
        results = [
            ("a", _result(True)),
            ("b", _result(False)),
            ("c", _result(False)),
        ]
        assert merger.merge(results).action == Action.ALLOW

    def test_tie_allows(self) -> None:
        """Strictly more than half must trigger. A tie is not enough."""
        merger = DecisionMerger(strategy="majority")
        results = [("a", _result(True)), ("b", _result(False))]
        assert merger.merge(results).action == Action.ALLOW


def test_unknown_strategy_raises() -> None:
    with pytest.raises(ValueError, match="Unknown strategy"):
        DecisionMerger(strategy="bogus")  # type: ignore[arg-type]


def test_contributing_detectors_and_reasons_populated() -> None:
    merger = DecisionMerger(strategy="unanimous")
    results = [
        ("detector_a", _result(True, reason="prompt injection")),
        ("detector_b", _result(True, reason="pii detected")),
    ]
    decision = merger.merge(results)
    assert decision.contributing_detectors == ["detector_a", "detector_b"]
    assert decision.reason_chain == ["prompt injection", "pii detected"]
