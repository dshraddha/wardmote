"""Core protocols for Wardmote.

This module defines the `Detector` Protocol, the central abstraction of the
library. Any class that has a `name`, `stages`, and a `detect` method with
the right signature is a valid detector — it does not need to inherit from
anything.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:  # pragma: no cover
    from wardmote.types import DetectorContext, DetectorResult, Stage


@runtime_checkable
class Detector(Protocol):
    """A security detector that inspects content at one or more pipeline stages.

    To be a valid detector, a class must provide:

    - ``name``: a short, stable identifier (used in logs and decisions)
    - ``stages``: a frozenset of ``Stage`` values where the detector runs
    - ``detect``: a method that inspects content and returns a ``DetectorResult``

    No inheritance is required. The class does not need to know Wardmote exists.
    """

    name: str
    stages: frozenset[Stage]

    def detect(self, content: str, context: DetectorContext) -> DetectorResult:
        """Inspect ``content`` and return a ``DetectorResult``.

        Implementations must be:

        - **Pure**: no side effects on external state during detection.
        - **Deterministic**: the same input produces the same result.
        - **Non-raising**: if detection fails internally, return a result
          with ``triggered=False`` rather than raising an exception.
        """
        ...  # pragma: no cover
