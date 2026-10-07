"""Deterministic packet-window rules for possible scans and high traffic rates."""

from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict
from math import isfinite
from numbers import Integral

import pandas as pd

from analyzer.contracts import DetectionConfig


def _window_nanoseconds(seconds: float) -> int:
    if not isfinite(seconds) or seconds <= 0:
        raise ValueError("Detection windows must be finite and positive.")
    try:
        nanoseconds = pd.Timedelta(seconds=seconds).value
    except (ValueError, OverflowError) as exc:
        raise ValueError("Detection window is outside the supported time range.") from exc
    if nanoseconds <= 0:
        raise ValueError("Detection windows must be at least one nanosecond.")
    return nanoseconds


def _timestamp_nanoseconds(value: object) -> int | None:
    try:
        timestamp = pd.Timestamp(value)
        if pd.isna(timestamp) or timestamp.tzinfo is None:
            return None
        return timestamp.tz_convert("UTC").value
    except (TypeError, ValueError, OverflowError):
        return None


def _initial_syn(flags: object) -> bool:
    if not isinstance(flags, str):
        return False
    return "S" in flags and "A" not in flags and set(flags) <= set("FSRPAUECN")


def _utc_iso(nanoseconds: int) -> str:
    return pd.Timestamp(nanoseconds, tz="UTC").isoformat().replace("+00:00", "Z")


def _scan_window(
    events: list[tuple[int, int]], window_ns: int,
) -> tuple[int, int, int, int]:
    events.sort()
    times = [timestamp for timestamp, _ in events]
    ports: Counter[int] = Counter()
    left = 0
    best_rank: tuple[int, int, int] | None = None
    best_start = best_end = best_unique = 0

    for right, (end, port) in enumerate(events):
        ports[port] += 1
        while end - events[left][0] > window_ns:
            expired_port = events[left][1]
            ports[expired_port] -= 1
            if ports[expired_port] == 0:
                del ports[expired_port]
            left += 1

        # Redundant leading SYNs can be removed without losing any unique port.
        while left < right and ports[events[left][1]] > 1:
            ports[events[left][1]] -= 1
            left += 1

        start = events[left][0]
        rank = (-len(ports), end - start, start)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_start, best_end, best_unique = start, end, len(ports)

    # Include every SYN at the selected endpoints, including duplicate ports.
    syn_packets = bisect_right(times, best_end) - bisect_left(times, best_start)
    return best_start, best_end, best_unique, syn_packets


def _rate_window(times: list[int], window_ns: int) -> tuple[int, int, int]:
    times.sort()
    left = 0
    best_rank: tuple[int, int, int] | None = None
    best_start = best_end = best_count = 0

    for right, end in enumerate(times):
        while end - times[left] > window_ns:
            left += 1
        start = times[left]
        count = right - left + 1
        rank = (-count, end - start, start)
        if best_rank is None or rank < best_rank:
            best_rank = rank
            best_start, best_end, best_count = start, end, count

    return best_start, best_end, best_count


def detect_anomalies(
    packets: pd.DataFrame,
    config: DetectionConfig | None = None,
) -> list[dict[str, object]]:
    """Return strongest per-pair scan and per-source rate alerts without mutation.

    Window endpoints are inclusive. Ties prefer shorter duration, then earlier
    start. Unusable or timezone-naive timestamps are skipped. Configuration
    thresholds and windows must be positive; invalid settings raise ValueError.
    """
    if packets.empty:
        return []
    config = DetectionConfig() if config is None else config
    for threshold in (config.port_scan_unique_ports, config.high_rate_packets):
        if not isinstance(threshold, Integral) or isinstance(threshold, bool) or threshold <= 0:
            raise ValueError("Detection packet/port thresholds must be positive integers.")
    scan_ns = _window_nanoseconds(config.port_scan_window_seconds)
    rate_ns = _window_nanoseconds(config.high_rate_window_seconds)

    scan_groups: dict[tuple[str, str], list[tuple[int, int]]] = defaultdict(list)
    rate_groups: dict[str, list[int]] = defaultdict(list)
    columns = ["timestamp", "src_ip", "dst_ip", "dst_port", "transport", "tcp_flags"]
    for timestamp, source, destination, port, transport, flags in packets[columns].itertuples(
        index=False, name=None,
    ):
        if not isinstance(source, str) or not source:
            continue
        time_ns = _timestamp_nanoseconds(timestamp)
        if time_ns is None:
            continue
        rate_groups[source].append(time_ns)
        if (
            isinstance(transport, str)
            and transport == "TCP"
            and isinstance(destination, str)
            and bool(destination)
            and isinstance(port, Integral)
            and not isinstance(port, bool)
            and _initial_syn(flags)
        ):
            scan_groups[(source, destination)].append((time_ns, int(port)))

    alerts: list[dict[str, object]] = []
    for source, destination in sorted(scan_groups):
        start, end, unique_ports, syn_packets = _scan_window(
            scan_groups[(source, destination)], scan_ns,
        )
        if unique_ports < config.port_scan_unique_ports:
            continue
        alerts.append({
            "id": f"portscan-{source}-{destination}",
            "type": "POSSIBLE_PORT_SCAN",
            "severity": "HIGH",
            "source_ip": source,
            "destination_ip": destination,
            "start_time": _utc_iso(start),
            "end_time": _utc_iso(end),
            "evidence": {
                "unique_destination_ports": unique_ports,
                "window_seconds": config.port_scan_window_seconds,
                "syn_packets": syn_packets,
            },
            "message": (
                f"Possible port scan: {source} contacted {unique_ports} unique TCP "
                f"ports on {destination} within {config.port_scan_window_seconds:g} seconds."
            ),
        })

    for source in sorted(rate_groups):
        start, end, count = _rate_window(rate_groups[source], rate_ns)
        if count < config.high_rate_packets:
            continue
        alerts.append({
            "id": f"highrate-{source}",
            "type": "HIGH_PACKET_RATE",
            "severity": "MEDIUM",
            "source_ip": source,
            "destination_ip": None,
            "start_time": _utc_iso(start),
            "end_time": _utc_iso(end),
            "evidence": {
                "packets": count,
                "window_seconds": config.high_rate_window_seconds,
                "packets_per_second": count / config.high_rate_window_seconds,
            },
            "message": (
                f"Potential high-rate traffic: {source} generated {count} packets "
                f"within {config.high_rate_window_seconds:g} seconds."
            ),
        })
    return alerts
