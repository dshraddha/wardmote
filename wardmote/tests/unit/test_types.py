"""Tests for wardmote.types."""

import dataclasses

import pytest

from wardmote.types import Action, Decision, DetectorResult, Stage


def test_stage_values() -> None:
    assert Stage.INPUT.value == "input"
    assert Stage.OUTPUT.value == "output"


def test_detector_result_is_immutable() -> None:
    result = DetectorResult(triggered=True, confidence=0.95)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.triggered = False  # type: ignore[misc]


def test_decision_defaults() -> None:
    decision = Decision(action=Action.ALLOW)
    assert decision.contributing_detectors == []
    assert decision.reason_chain == []


def test_all_actions_exist() -> None:
    assert Action.ALLOW.value == "allow"
    assert Action.BLOCK.value == "block"
    assert Action.REDACT.value == "redact"
    assert Action.FLAG.value == "flag"
