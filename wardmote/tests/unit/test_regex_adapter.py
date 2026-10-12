"""Tests for wardmote.adapters.regex."""

import re

import pytest

from wardmote import RegexDetector, Stage


class TestRegexDetectorMatching:
    def test_no_patterns_match(self) -> None:
        detector = RegexDetector(patterns={"aws_key": r"AKIA[0-9A-Z]{16}"})
        result = detector.detect("just some text", {})
        assert result.triggered is False
        assert result.reason is None

    def test_single_pattern_matches(self) -> None:
        detector = RegexDetector(patterns={"aws_key": r"AKIA[0-9A-Z]{16}"})
        result = detector.detect("my key is AKIAIOSFODNN7EXAMPLE", {})
        assert result.triggered is True
        assert result.reason == "matched: aws_key"

    def test_multiple_patterns_multiple_matches(self) -> None:
        detector = RegexDetector(
            patterns={
                "aws_key": r"AKIA[0-9A-Z]{16}",
                "email": r"[\w.+-]+@[\w-]+\.[\w.-]+",
            }
        )
        result = detector.detect("contact alice@example.com with key AKIAIOSFODNN7EXAMPLE", {})
        assert result.triggered is True
        assert result.reason is not None
        assert "aws_key" in result.reason
        assert "email" in result.reason

    def test_confidence_is_one_when_triggered(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"})
        result = detector.detect("foo", {})
        assert result.confidence == 1.0

    def test_confidence_is_one_when_not_triggered(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"})
        result = detector.detect("bar", {})
        assert result.confidence == 1.0


class TestRegexDetectorConfiguration:
    def test_empty_patterns_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one pattern"):
            RegexDetector(patterns={})

    def test_invalid_regex_raises_with_pattern_name(self) -> None:
        with pytest.raises(ValueError, match="Invalid regex for pattern 'broken'"):
            RegexDetector(patterns={"broken": r"(unclosed"})

    def test_custom_name_overrides_default(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"}, name="my_detector")
        assert detector.name == "my_detector"

    def test_default_name_is_regex(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"})
        assert detector.name == "regex"

    def test_ignorecase_flag_is_applied(self) -> None:
        detector = RegexDetector(
            patterns={"foo": r"foo"},
            flags=re.IGNORECASE,
        )
        result = detector.detect("FOO", {})
        assert result.triggered is True

    def test_flags_are_keyword_only(self) -> None:
        """Passing flags positionally should be a TypeError."""
        with pytest.raises(TypeError):
            RegexDetector({"foo": r"foo"}, True)  # type: ignore[misc]


class TestRegexDetectorProtocolConformance:
    def test_has_expected_name_attribute(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"})
        assert hasattr(detector, "name")
        assert isinstance(detector.name, str)

    def test_stages_includes_input_and_output(self) -> None:
        detector = RegexDetector(patterns={"foo": r"foo"})
        assert Stage.INPUT in detector.stages
        assert Stage.OUTPUT in detector.stages
