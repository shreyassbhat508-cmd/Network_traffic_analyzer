"""Service contracts and offline capture integration; no live network access."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from decimal import Decimal
import inspect
import io
from pathlib import Path
import struct
import tempfile

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from scapy.layers.inet import IP, TCP, UDP
from scapy.layers.l2 import Ether
from scapy.packet import Packet
from scapy.utils import PcapNgWriter, PcapWriter

import analyzer.service as service
from analyzer.anomaly_detector import detect_anomalies
from analyzer.contracts import (
    MAX_FILE_BYTES,
    MAX_PACKETS,
    PACKET_COLUMNS,
    PROTOCOL_ORDER,
    DetectionConfig,
)
from analyzer.service import analyze_capture
from analyzer.parser import parse_capture_bytes
from analyzer.statistics import calculate_statistics


BASE_TIME = pd.Timestamp("2026-10-07T04:40:00Z")
RESULT_KEYS = {
    "schema_version", "metadata", "summary", "protocol_distribution",
    "top_sources", "top_destinations", "packet_sizes", "timeline", "alerts", "packets",
}
PARSER_METADATA_KEYS = {
    "filename", "file_size_bytes", "format", "parsed_packets", "truncated", "warnings",
}
METADATA_KEYS = PARSER_METADATA_KEYS | {"start_time", "end_time", "duration_seconds"}
SUMMARY_KEYS = {
    "total_packets", "total_bytes", "average_packet_size", "min_packet_size",
    "max_packet_size", "unique_sources", "unique_destinations", "alert_count",
}
STATISTICS_SECTIONS = (
    "protocol_distribution", "top_sources", "top_destinations", "packet_sizes", "timeline",
)


def _traffic(
    count: int,
    *,
    source: str = "10.0.0.50",
    scan: bool = False,
    udp: bool = False,
    seconds: list[float] | None = None,
) -> list[Packet]:
    offsets = [index / 100 for index in range(count)] if seconds is None else seconds
    packets = []
    for index, offset in enumerate(offsets):
        transport = UDP(sport=50000, dport=8000) if udp else TCP(
            sport=50000, dport=1000 + index if scan else 80, flags="S" if scan else "A",
        )
        packet = (
            Ether(src="00:11:22:33:44:55", dst="66:77:88:99:aa:bb")
            / IP(src=source, dst="10.0.0.10") / transport
        )
        packet.time = Decimal(int(BASE_TIME.timestamp())) + Decimal(str(offset))
        packets.append(packet)
    return packets


def _pcap_bytes(packets: list[Packet]) -> bytes:
    stream = io.BytesIO()
    writer = PcapWriter(stream, linktype=1)
    try:
        for packet in packets:
            writer.write(packet)
        writer.flush()
        return stream.getvalue()
    finally:
        writer.close()


@pytest.fixture
def tiny_capture() -> bytes:
    return _pcap_bytes(_traffic(3, seconds=[4.0, 0.0, 1.5]))


def _assert_result_contract(result: dict[str, object]) -> None:
    assert set(result) == RESULT_KEYS
    assert result["schema_version"] == "1.0"
    assert set(result["metadata"]) == METADATA_KEYS
    assert set(result["summary"]) == SUMMARY_KEYS
    assert isinstance(result["packets"], pd.DataFrame)
    assert list(result["packets"].columns) == PACKET_COLUMNS
    assert result["summary"]["alert_count"] == len(result["alerts"])


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


def test_frozen_service_signature() -> None:
    assert callable(analyze_capture)
    signature = inspect.signature(analyze_capture)
    assert list(signature.parameters) == ["data", "filename", "config"]
    assert signature.parameters["config"].default is None
    assert all(p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD for p in signature.parameters.values())


def test_empty_bytes_raise_value_error() -> None:
    with pytest.raises(ValueError, match="empty"):
        analyze_capture(b"", "empty.pcap")


def test_oversized_input_is_rejected_before_parsing(monkeypatch: pytest.MonkeyPatch) -> None:
    def unexpected_parser_call(*args, **kwargs):
        pytest.fail("Oversized data must be rejected before parsing.")

    monkeypatch.setattr(service, "parse_capture_bytes", unexpected_parser_call)
    with pytest.raises(ValueError, match="maximum file size"):
        analyze_capture(b"x" * (MAX_FILE_BYTES + 1), "oversized.pcap")


def test_valid_tiny_pcap_returns_complete_result(tiny_capture: bytes) -> None:
    result = analyze_capture(tiny_capture, "tiny.pcap")
    _assert_result_contract(result)
    packets, parser_metadata = parse_capture_bytes(tiny_capture, "tiny.pcap")
    stats = calculate_statistics(packets)
    assert_frame_equal(result["packets"], packets)
    for key in PARSER_METADATA_KEYS:
        assert result["metadata"][key] == parser_metadata[key]
    assert result["summary"] == {**stats["summary"], "alert_count": 0}
    for section in STATISTICS_SECTIONS:
        assert result[section] == stats[section]
    assert result["alerts"] == []


def test_timing_uses_earliest_and_latest_unsorted_packets(tiny_capture: bytes) -> None:
    metadata = analyze_capture(tiny_capture, "unsorted.pcap")["metadata"]
    assert metadata["start_time"] == "2026-10-07T04:40:00Z"
    assert metadata["end_time"] == "2026-10-07T04:40:04Z"
    assert metadata["duration_seconds"] == 4.0
    assert isinstance(metadata["duration_seconds"], float)


def test_single_packet_has_zero_duration() -> None:
    metadata = analyze_capture(_pcap_bytes(_traffic(1)), "one.pcap")["metadata"]
    assert metadata["start_time"] == metadata["end_time"] == "2026-10-07T04:40:00Z"
    assert metadata["duration_seconds"] == 0.0


def test_synthetic_scan_capture() -> None:
    result = analyze_capture(_pcap_bytes(_traffic(120, scan=True)), "scan.pcap")
    assert [alert["type"] for alert in result["alerts"]] == ["POSSIBLE_PORT_SCAN"]
    assert result["summary"]["alert_count"] == 1
    assert result["alerts"][0]["evidence"]["unique_destination_ports"] == 120


def test_synthetic_high_rate_capture() -> None:
    result = analyze_capture(_pcap_bytes(_traffic(356, udp=True)), "rate.pcap")
    assert [alert["type"] for alert in result["alerts"]] == ["HIGH_PACKET_RATE"]
    assert result["summary"]["alert_count"] == 1
    assert result["alerts"][0]["evidence"]["packets"] == 356


def test_combined_suspicious_capture() -> None:
    capture = _pcap_bytes(
        _traffic(120, scan=True) + _traffic(356, udp=True, source="10.0.0.60"),
    )
    result = analyze_capture(capture, "combined.pcap")
    _assert_result_contract(result)
    assert [alert["type"] for alert in result["alerts"]] == ["POSSIBLE_PORT_SCAN", "HIGH_PACKET_RATE"]
    assert result["summary"]["alert_count"] == 2


def test_custom_detection_config_is_respected() -> None:
    capture = _pcap_bytes(_traffic(3, scan=True, seconds=[0.0, 2.0, 4.0]))
    assert analyze_capture(capture, "custom.pcap")["alerts"] == []
    config = DetectionConfig(3, 4.0, 3, 4.0)
    result = analyze_capture(capture, "custom.pcap", config)
    assert [alert["type"] for alert in result["alerts"]] == ["POSSIBLE_PORT_SCAN", "HIGH_PACKET_RATE"]
    assert result["summary"]["alert_count"] == 2


@pytest.mark.parametrize("data", [b"not a capture", b"\xd4\xc3\xb2\xa1\x02\x00", b"\x0a\x0d\x0d\x0a"])
def test_corrupt_capture_raises_useful_value_error(data: bytes) -> None:
    with pytest.raises(ValueError, match="[Cc]orrupt.*broken"):
        analyze_capture(data, "broken.pcap")


def test_valid_zero_packet_capture_returns_complete_result() -> None:
    header = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    result = analyze_capture(header, "zero.pcap")
    _assert_result_contract(result)
    assert result["packets"].empty
    assert result["summary"]["total_packets"] == result["summary"]["total_bytes"] == 0
    assert result["summary"]["alert_count"] == 0
    assert result["alerts"] == []
    assert result["metadata"]["start_time"] is None
    assert result["metadata"]["end_time"] is None
    assert result["metadata"]["duration_seconds"] == 0.0
    stats = calculate_statistics(result["packets"])
    for section in STATISTICS_SECTIONS:
        assert result[section] == stats[section]


def test_truncation_and_warning_identity_are_preserved(
    monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes,
) -> None:
    parsed = []

    def limited_parser(data: bytes, filename: str):
        output = parse_capture_bytes(data, filename, max_packets=2)
        parsed.append(output)
        return output

    monkeypatch.setattr(service, "parse_capture_bytes", limited_parser)
    result = analyze_capture(tiny_capture, "truncated.pcap")
    packets, metadata = parsed[0]
    assert result["packets"] is packets
    assert len(packets) == 2
    assert result["metadata"]["truncated"] is True
    assert result["metadata"]["warnings"] is metadata["warnings"]
    assert metadata["warnings"] == ["Capture truncated at max_packets limit of 2."]
    for key in PARSER_METADATA_KEYS:
        assert result["metadata"][key] == metadata[key]
    assert result["metadata"]["duration_seconds"] == 4.0


@pytest.mark.parametrize("config", [None, DetectionConfig(1, 1.0, 1, 1.0)])
def test_orchestration_order_identity_and_input_preservation(
    monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes, config: DetectionConfig | None,
) -> None:
    packets, metadata = parse_capture_bytes(tiny_capture, "identity.pcap")
    original = packets.copy(deep=True)
    original_metadata = deepcopy(metadata)
    stats = calculate_statistics(packets)
    original_summary = stats["summary"].copy()
    alerts = detect_anomalies(packets, config)
    calls = []

    def parser(data, filename):
        assert data is tiny_capture
        assert filename == "identity.pcap"
        calls.append("parse")
        return packets, metadata

    def statistics(frame):
        assert frame is packets
        calls.append("statistics")
        return stats

    def detector(frame, supplied_config):
        assert frame is packets
        assert supplied_config is config
        calls.append("anomalies")
        return alerts

    monkeypatch.setattr(service, "parse_capture_bytes", parser)
    monkeypatch.setattr(service, "calculate_statistics", statistics)
    monkeypatch.setattr(service, "detect_anomalies", detector)
    result = analyze_capture(tiny_capture, "identity.pcap", config)
    assert calls == ["parse", "statistics", "anomalies"]
    assert result["packets"] is packets
    assert result["alerts"] is alerts
    for section in STATISTICS_SECTIONS:
        assert result[section] is stats[section]
    assert result["summary"]["alert_count"] == len(alerts)
    assert_frame_equal(packets, original)
    assert metadata == original_metadata
    assert stats["summary"] == original_summary


def test_exact_file_size_limit_is_accepted(
    monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes,
) -> None:
    packets, metadata = parse_capture_bytes(tiny_capture, "boundary.pcap")
    payload = b"x" * MAX_FILE_BYTES
    metadata["file_size_bytes"] = len(payload)

    def parser(data, filename):
        assert data is payload
        return packets, metadata

    monkeypatch.setattr(service, "parse_capture_bytes", parser)
    result = analyze_capture(payload, "boundary.pcap")
    assert result["metadata"]["file_size_bytes"] == MAX_FILE_BYTES


def test_parser_value_error_is_propagated_unchanged(monkeypatch: pytest.MonkeyPatch) -> None:
    error = ValueError("Corrupt capture: original parser detail")

    def parser(data, filename):
        raise error

    monkeypatch.setattr(service, "parse_capture_bytes", parser)
    with pytest.raises(ValueError) as caught:
        analyze_capture(b"capture", "broken.pcap")
    assert caught.value is error


def test_programming_errors_are_not_hidden(monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes) -> None:
    error = RuntimeError("Unexpected statistics bug")

    def statistics(packets):
        raise error

    monkeypatch.setattr(service, "calculate_statistics", statistics)
    with pytest.raises(RuntimeError) as caught:
        analyze_capture(tiny_capture, "bug.pcap")
    assert caught.value is error


def test_nat_packet_timestamps_are_handled_without_mutation(
    monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes,
) -> None:
    packets, metadata = parse_capture_bytes(tiny_capture, "nat.pcap")
    packets.loc[0, "timestamp"] = pd.NaT
    original = packets.copy(deep=True)
    monkeypatch.setattr(service, "parse_capture_bytes", lambda data, filename: (packets, metadata))
    result = analyze_capture(tiny_capture, "nat.pcap")
    assert result["metadata"]["start_time"] == "2026-10-07T04:40:00Z"
    assert result["metadata"]["end_time"] == "2026-10-07T04:40:01.500000Z"
    assert result["metadata"]["duration_seconds"] == 1.5
    assert_frame_equal(packets, original)


def test_all_nat_timestamps_produce_null_timing(
    monkeypatch: pytest.MonkeyPatch, tiny_capture: bytes,
) -> None:
    packets, metadata = parse_capture_bytes(tiny_capture, "all_nat.pcap")
    packets["timestamp"] = pd.Series(pd.NaT, index=packets.index, dtype="datetime64[ns, UTC]")
    monkeypatch.setattr(service, "parse_capture_bytes", lambda data, filename: (packets, metadata))
    result = analyze_capture(tiny_capture, "all_nat.pcap")
    assert result["metadata"]["start_time"] is result["metadata"]["end_time"] is None
    assert result["metadata"]["duration_seconds"] == 0.0
    assert result["summary"]["total_packets"] == 3


def test_timing_helper_coerces_unusable_values_and_normalizes_utc() -> None:
    frame = pd.DataFrame({"timestamp": [None, "invalid", [], "2026-10-07T10:10:00+05:30", BASE_TIME + pd.Timedelta(seconds=4)]})
    original = frame.copy(deep=True)
    assert service._capture_timing(frame) == ("2026-10-07T04:40:00Z", "2026-10-07T04:40:04Z", 4.0)
    assert_frame_equal(frame, original)


def test_valid_pcapng_service_result() -> None:
    with tempfile.NamedTemporaryFile(suffix=".pcapng", delete=False) as temporary:
        path = Path(temporary.name)
    try:
        writer = PcapNgWriter(str(path))
        try:
            for packet in _traffic(2, udp=True):
                writer.write(packet)
        finally:
            writer.close()
        result = analyze_capture(path.read_bytes(), "service.pcapng")
    finally:
        path.unlink()
    _assert_result_contract(result)
    assert result["metadata"]["format"] == "PCAPNG"
    assert result["summary"]["total_packets"] == 2
    assert result["alerts"] == []
