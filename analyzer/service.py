"""Public service interface; orchestration will be added during integration."""

from analyzer.contracts import DetectionConfig


def analyze_capture(
    data: bytes,
    filename: str,
    config: DetectionConfig | None = None,
) -> dict[str, object]:
    """Analyze a capture once the backend modules are integrated.

    This temporary stub raises explicitly and never returns fabricated results.
    Parser, statistics, and anomaly implementations are not yet required imports.
    """
    raise NotImplementedError(
        "Capture analysis orchestration will be implemented during integration."
    )
