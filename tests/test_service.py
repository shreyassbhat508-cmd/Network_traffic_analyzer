"""Smoke tests for the frozen contracts and temporary service interface."""

from dataclasses import FrozenInstanceError

import pytest

from analyzer.contracts import (
    MAX_FILE_BYTES,
    MAX_PACKETS,
    PACKET_COLUMNS,
    PROTOCOL_ORDER,
    DetectionConfig,
)
from analyzer.service import analyze_capture


def test_frozen_packet_and_protocol_order() -> None:
    assert PACKET_COLUMNS == [
        "timestamp",
        "src_ip",
        "dst_ip",
        "src_port",
        "dst_port",
        "protocol",
        "transport",
        "length",
        "tcp_flags",
        "ip_version",
        "dns_query",
    ]
    assert PROTOCOL_ORDER == ["TCP", "UDP", "ICMP", "DNS", "OTHER"]


def test_capture_limits() -> None:
    assert MAX_FILE_BYTES == 25 * 1024 * 1024
    assert MAX_PACKETS == 100_000


def test_detection_config_defaults_and_frozen_state() -> None:
    config = DetectionConfig()
    assert config.port_scan_unique_ports == 100
    assert config.port_scan_window_seconds == 60.0
    assert config.high_rate_packets == 300
    assert config.high_rate_window_seconds == 10.0
    with pytest.raises(FrozenInstanceError):
        setattr(config, "high_rate_packets", 301)


def test_service_stub_is_callable_and_explicitly_unimplemented() -> None:
    assert callable(analyze_capture)
    with pytest.raises(NotImplementedError, match="during integration"):
        analyze_capture(b"", "smoke.pcap")
