"""Orchestrate capture parsing, statistics, and deterministic anomaly detection."""

import pandas as pd

from analyzer.anomaly_detector import detect_anomalies
from analyzer.contracts import MAX_FILE_BYTES, DetectionConfig
from analyzer.parser import parse_capture_bytes
from analyzer.statistics import calculate_statistics


def _capture_timing(packets: pd.DataFrame) -> tuple[str | None, str | None, float]:
    timestamps = pd.to_datetime(
        packets["timestamp"], utc=True, errors="coerce", format="mixed",
    ).dropna()
    if timestamps.empty:
        return None, None, 0.0
    start, end = timestamps.min(), timestamps.max()
    return (
        start.isoformat().replace("+00:00", "Z"),
        end.isoformat().replace("+00:00", "Z"),
        float((end - start).total_seconds()),
    )


def analyze_capture(
    data: bytes,
    filename: str,
    config: DetectionConfig | None = None,
) -> dict[str, object]:
    """Return the frozen analysis result while preserving module outputs.

    Empty uploads, oversized uploads, and parser errors raise ValueError.
    Timing ignores unusable timestamps; naive values, if present, assume UTC.
    """
    if not data:
        raise ValueError("Capture data is empty; provide a non-empty PCAP or PCAPNG file.")
    if len(data) > MAX_FILE_BYTES:
        raise ValueError(f"Capture exceeds the maximum file size of {MAX_FILE_BYTES} bytes.")

    packets, parser_metadata = parse_capture_bytes(data, filename)
    statistics = calculate_statistics(packets)
    alerts = detect_anomalies(packets, config)
    start_time, end_time, duration_seconds = _capture_timing(packets)

    metadata = {
        "filename": parser_metadata["filename"],
        "file_size_bytes": parser_metadata["file_size_bytes"],
        "format": parser_metadata["format"],
        "parsed_packets": parser_metadata["parsed_packets"],
        "truncated": parser_metadata["truncated"],
        "start_time": start_time,
        "end_time": end_time,
        "duration_seconds": duration_seconds,
        "warnings": parser_metadata["warnings"],
    }
    summary = dict(statistics["summary"])
    summary["alert_count"] = len(alerts)

    return {
        "schema_version": "1.0",
        "metadata": metadata,
        "summary": summary,
        "protocol_distribution": statistics["protocol_distribution"],
        "top_sources": statistics["top_sources"],
        "top_destinations": statistics["top_destinations"],
        "packet_sizes": statistics["packet_sizes"],
        "timeline": statistics["timeline"],
        "alerts": alerts,
        "packets": packets,
    }
