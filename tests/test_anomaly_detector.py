"""Contract and window-boundary tests using packet DataFrames, without a parser."""

from datetime import datetime
from random import Random

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from analyzer.anomaly_detector import detect_anomalies
from analyzer.contracts import PACKET_COLUMNS, DetectionConfig


BASE_TIME = pd.Timestamp("2026-10-07T04:40:00Z")
SOURCE = "10.0.0.50"
DESTINATION = "10.0.0.10"
ALERT_KEYS = {
    "id", "type", "severity", "source_ip", "destination_ip",
    "start_time", "end_time", "evidence", "message",
}


def _packets(
    count: int,
    *,
    seconds: list[float] | None = None,
    ports: list[int] | None = None,
    source: str = SOURCE,
    destination: str = DESTINATION,
    transport: str = "TCP",
    flags: str | None = "S",
) -> pd.DataFrame:
    seconds = [index / 100 for index in range(count)] if seconds is None else seconds
    ports = list(range(count)) if ports is None else ports
    rows = [{
        "timestamp": BASE_TIME + pd.Timedelta(seconds=seconds[index]),
        "src_ip": source,
        "dst_ip": destination,
        "src_port": 50000,
        "dst_port": ports[index],
        "protocol": transport,
        "transport": transport,
        "length": 60,
        "tcp_flags": flags,
        "ip_version": 4,
        "dns_query": None,
    } for index in range(count)]
    frame = pd.DataFrame(rows, columns=PACKET_COLUMNS)
    frame["timestamp"] = pd.Series(frame["timestamp"], dtype="datetime64[ns, UTC]")
    for column in ("src_port", "dst_port", "ip_version"):
        frame[column] = frame[column].astype("Int64")
    frame["length"] = frame["length"].astype("int64")
    for column in ("src_ip", "dst_ip", "protocol", "transport", "tcp_flags", "dns_query"):
        frame[column] = frame[column].astype(object)
    return frame


def _alerts_of_type(packets: pd.DataFrame, kind: str) -> list[dict[str, object]]:
    return [alert for alert in detect_anomalies(packets) if alert["type"] == kind]


def test_empty_packets() -> None:
    assert detect_anomalies(_packets(0)) == []
    assert detect_anomalies(pd.DataFrame()) == []


@pytest.mark.parametrize("count,expected", [(99, 0), (100, 1), (120, 1)])
def test_default_scan_threshold(count: int, expected: int) -> None:
    alerts = _alerts_of_type(_packets(count), "POSSIBLE_PORT_SCAN")
    assert len(alerts) == expected
    if alerts:
        assert alerts[0]["evidence"] == {
            "unique_destination_ports": count, "window_seconds": 60.0,
            "syn_packets": count,
        }


def test_repeated_syns_do_not_inflate_unique_ports() -> None:
    assert _alerts_of_type(_packets(200, ports=list(range(99)) + [80] * 101), "POSSIBLE_PORT_SCAN") == []


def test_duplicate_syns_are_included_in_evidence() -> None:
    packets = _packets(110, seconds=[0.0] * 110, ports=list(range(100)) + [80] * 10)
    alert = _alerts_of_type(packets, "POSSIBLE_PORT_SCAN")[0]
    assert alert["evidence"]["unique_destination_ports"] == 100
    assert alert["evidence"]["syn_packets"] == 110


@pytest.mark.parametrize("flags", ["SA", "A", "PA", None, pd.NA, 2, [], "SYN", "garbage"])
def test_non_initial_or_malformed_flags_do_not_count(flags: object) -> None:
    packets = _packets(100)
    packets.at[99, "tcp_flags"] = flags
    assert _alerts_of_type(packets, "POSSIBLE_PORT_SCAN") == []


@pytest.mark.parametrize("count,expected", [(299, 0), (300, 1), (356, 1)])
def test_default_rate_threshold(count: int, expected: int) -> None:
    alerts = _alerts_of_type(_packets(count, transport="UDP", flags=None), "HIGH_PACKET_RATE")
    assert len(alerts) == expected
    if alerts:
        assert alerts[0]["evidence"] == {
            "packets": count, "window_seconds": 10.0,
            "packets_per_second": count / 10.0,
        }


def test_unsorted_timestamps_and_duplicate_indices_are_supported() -> None:
    packets = _packets(300).sample(frac=1, random_state=7)
    expected = detect_anomalies(_packets(300))
    packets.index = [0] * len(packets)
    assert detect_anomalies(packets) == expected


def test_null_ips_ports_and_flags_do_not_crash_or_count_as_scan() -> None:
    packets = _packets(100)
    packets.at[96, "src_ip"] = None
    packets.at[97, "dst_ip"] = None
    packets.at[98, "dst_port"] = pd.NA
    packets.at[99, "tcp_flags"] = None
    assert detect_anomalies(packets) == []


def test_non_ip_packets_are_ignored() -> None:
    packets = _packets(300, transport="OTHER", flags=None)
    packets["src_ip"] = None
    packets["dst_ip"] = None
    packets["src_port"] = pd.Series(pd.NA, index=packets.index, dtype="Int64")
    packets["dst_port"] = pd.Series(pd.NA, index=packets.index, dtype="Int64")
    packets["ip_version"] = pd.Series(pd.NA, index=packets.index, dtype="Int64")
    assert detect_anomalies(packets) == []


def test_non_tcp_packets_do_not_count_as_scans() -> None:
    assert detect_anomalies(_packets(120, transport="UDP")) == []


def test_null_destination_and_transport_still_count_for_rate() -> None:
    packets = _packets(300, transport="OTHER", flags=None)
    packets["dst_ip"] = None
    packets["transport"] = pd.NA
    packets["dst_port"] = pd.Series(pd.NA, index=packets.index, dtype="Int64")
    alerts = detect_anomalies(packets)
    assert len(alerts) == 1
    assert alerts[0]["type"] == "HIGH_PACKET_RATE"


def test_input_is_not_mutated() -> None:
    packets = _packets(300).sample(frac=1, random_state=4)
    original = packets.copy(deep=True)
    detect_anomalies(packets)
    assert_frame_equal(packets, original)


def test_custom_thresholds_and_window_lengths() -> None:
    packets = _packets(4, seconds=[0.0, 2.0, 4.0, 6.0])
    config = DetectionConfig(
        port_scan_unique_ports=3, port_scan_window_seconds=4.0,
        high_rate_packets=4, high_rate_window_seconds=6.0,
    )
    scan, rate = detect_anomalies(packets, config)
    assert scan["evidence"]["unique_destination_ports"] == 3
    assert scan["evidence"]["window_seconds"] == 4.0
    assert rate["evidence"] == {"packets": 4, "window_seconds": 6.0, "packets_per_second": 4 / 6}
    assert detect_anomalies(packets, DetectionConfig(3, 3.0, 4, 5.0)) == []


def test_only_strongest_scan_window_is_returned_per_pair() -> None:
    packets = _packets(220, seconds=[float(i) / 10 for i in range(100)] + [100.0 + i / 10 for i in range(120)])
    alerts = _alerts_of_type(packets, "POSSIBLE_PORT_SCAN")
    assert len(alerts) == 1
    assert alerts[0]["evidence"]["unique_destination_ports"] == 120
    assert alerts[0]["start_time"] == "2026-10-07T04:41:40Z"


def test_only_strongest_rate_window_is_returned_per_source() -> None:
    packets = _packets(656, transport="UDP", seconds=[i / 100 for i in range(300)] + [30.0 + i / 100 for i in range(356)])
    alerts = _alerts_of_type(packets, "HIGH_PACKET_RATE")
    assert len(alerts) == 1
    assert alerts[0]["evidence"]["packets"] == 356
    assert alerts[0]["start_time"] == "2026-10-07T04:40:30Z"


def test_scan_ties_prefer_shorter_then_earlier_window() -> None:
    packets = _packets(7, seconds=[0.0, 1.0, 2.0, 100.0, 100.5, 200.0, 200.5], ports=[1, 1, 2, 3, 4, 5, 6])
    scan = detect_anomalies(packets, DetectionConfig(2, 10.0, 1000, 10.0))[0]
    assert scan["start_time"] == "2026-10-07T04:41:40Z"
    assert scan["end_time"] == "2026-10-07T04:41:40.500000Z"


def test_redundant_leading_syns_do_not_lengthen_best_scan_window() -> None:
    packets = _packets(3, seconds=[0.0, 1.0, 2.0], ports=[1, 1, 2])
    scan = detect_anomalies(packets, DetectionConfig(2, 60.0, 1000, 10.0))[0]
    assert scan["start_time"] == "2026-10-07T04:40:01Z"
    assert scan["evidence"]["syn_packets"] == 2


def test_rate_ties_prefer_shorter_then_earlier_window() -> None:
    packets = _packets(6, seconds=[0.0, 2.0, 20.0, 21.0, 40.0, 41.0], transport="UDP")
    rate = detect_anomalies(packets, DetectionConfig(100, 60.0, 2, 5.0))[0]
    assert rate["start_time"] == "2026-10-07T04:40:20Z"
    assert rate["end_time"] == "2026-10-07T04:40:21Z"


@pytest.mark.parametrize("boundary,expected", [(60.0, 1), (60.000000001, 0)])
def test_scan_window_boundary_is_inclusive(boundary: float, expected: int) -> None:
    packets = _packets(100, seconds=[0.0] * 99 + [boundary])
    assert len(_alerts_of_type(packets, "POSSIBLE_PORT_SCAN")) == expected


@pytest.mark.parametrize("boundary,expected", [(10.0, 1), (10.000000001, 0)])
def test_rate_window_boundary_is_inclusive(boundary: float, expected: int) -> None:
    packets = _packets(300, seconds=[0.0] * 299 + [boundary], transport="UDP")
    assert len(_alerts_of_type(packets, "HIGH_PACKET_RATE")) == expected


@pytest.mark.parametrize("invalid", [pd.NaT, None, "invalid", pd.Timestamp("2026-10-07"), []])
def test_unusable_timestamps_ignore_only_affected_rows(invalid: object) -> None:
    packets = _packets(4)
    packets["timestamp"] = packets["timestamp"].astype(object)
    packets.at[3, "timestamp"] = invalid
    alerts = detect_anomalies(packets, DetectionConfig(3, 60.0, 3, 10.0))
    assert len(alerts) == 2
    assert alerts[0]["evidence"]["unique_destination_ports"] == 3
    assert alerts[1]["evidence"]["packets"] == 3


def test_alert_contract_types_evidence_ids_and_utc_times() -> None:
    packets = _packets(300)
    packets["timestamp"] = packets["timestamp"].dt.tz_convert("Asia/Kolkata")
    scan, rate = detect_anomalies(packets)
    for alert in (scan, rate):
        assert set(alert) == ALERT_KEYS
        for key in ALERT_KEYS - {"evidence", "destination_ip"}:
            assert isinstance(alert[key], str)
        assert isinstance(alert["evidence"], dict)
        for key in ("start_time", "end_time"):
            assert alert[key].endswith("Z")
            assert datetime.fromisoformat(alert[key]).utcoffset().total_seconds() == 0
        assert alert["start_time"] == "2026-10-07T04:40:00Z"
    assert scan["type"] == "POSSIBLE_PORT_SCAN"
    assert scan["severity"] == "HIGH"
    assert scan["id"] == f"portscan-{SOURCE}-{DESTINATION}"
    assert scan["destination_ip"] == DESTINATION
    assert set(scan["evidence"]) == {"unique_destination_ports", "window_seconds", "syn_packets"}
    assert rate["type"] == "HIGH_PACKET_RATE"
    assert rate["severity"] == "MEDIUM"
    assert rate["id"] == f"highrate-{SOURCE}"
    assert rate["destination_ip"] is None
    assert set(rate["evidence"]) == {"packets", "window_seconds", "packets_per_second"}
    assert scan["message"].startswith("Possible port scan:")
    assert rate["message"].startswith("Potential high-rate traffic:")


def test_deterministic_ordering_groups_and_ipv6_ids() -> None:
    packets = pd.concat([
        _packets(3, source="2001:db8::1", destination="2001:db8::2"),
        _packets(3, source="10.0.0.2", destination="10.0.0.9"),
        _packets(3, source="10.0.0.1", destination="10.0.0.8"),
        _packets(3, source="10.0.0.1", destination="10.0.0.7"),
    ], ignore_index=True)
    packets.loc[packets["src_ip"].str.startswith("2001"), "ip_version"] = 6
    config = DetectionConfig(3, 60.0, 3, 10.0)
    expected = detect_anomalies(packets, config)
    assert detect_anomalies(packets.sample(frac=1, random_state=9), config) == expected
    assert [(a["type"], a["source_ip"], a["destination_ip"]) for a in expected] == [
        ("POSSIBLE_PORT_SCAN", "10.0.0.1", "10.0.0.7"),
        ("POSSIBLE_PORT_SCAN", "10.0.0.1", "10.0.0.8"),
        ("POSSIBLE_PORT_SCAN", "10.0.0.2", "10.0.0.9"),
        ("POSSIBLE_PORT_SCAN", "2001:db8::1", "2001:db8::2"),
        ("HIGH_PACKET_RATE", "10.0.0.1", None),
        ("HIGH_PACKET_RATE", "10.0.0.2", None),
        ("HIGH_PACKET_RATE", "2001:db8::1", None),
    ]
    assert expected[3]["id"] == "portscan-2001:db8::1-2001:db8::2"


def test_ports_on_different_destinations_are_not_combined() -> None:
    packets = pd.concat([
        _packets(50), _packets(50, destination="10.0.0.11", ports=list(range(50, 100))),
    ], ignore_index=True)
    assert detect_anomalies(packets) == []


def test_scan_uses_transport_independently_of_dns_display_category() -> None:
    packets = _packets(100, flags="SEC")
    packets["protocol"] = "DNS"
    assert len(_alerts_of_type(packets, "POSSIBLE_PORT_SCAN")) == 1


@pytest.mark.parametrize("seed", range(5))
def test_strongest_windows_match_small_exhaustive_reference(seed: int) -> None:
    random = Random(seed)
    seconds = [float(random.randrange(31)) for _ in range(25)]
    ports = [random.randrange(8) for _ in seconds]
    packets = _packets(len(seconds), seconds=seconds, ports=ports)
    config = DetectionConfig(3, 7.0, 4, 3.0)
    alerts = {alert["type"]: alert for alert in detect_anomalies(packets, config)}
    # Exhaustive checking is limited to this small independent test oracle.
    for kind, window, threshold in [
        ("POSSIBLE_PORT_SCAN", 7.0, 3), ("HIGH_PACKET_RATE", 3.0, 4),
    ]:
        candidates = []
        for start in sorted(set(seconds)):
            for end in sorted(set(seconds)):
                if not 0 <= end - start <= window:
                    continue
                active = [port for time, port in zip(seconds, ports) if start <= time <= end]
                count = len(set(active)) if kind == "POSSIBLE_PORT_SCAN" else len(active)
                candidates.append(((-count, end - start, start), start, end, count, len(active)))
        _, start, end, count, packet_count = min(candidates)
        if count < threshold:
            assert kind not in alerts
            continue
        alert = alerts[kind]
        assert pd.Timestamp(alert["start_time"]) == BASE_TIME + pd.Timedelta(seconds=start)
        assert pd.Timestamp(alert["end_time"]) == BASE_TIME + pd.Timedelta(seconds=end)
        if kind == "POSSIBLE_PORT_SCAN":
            assert alert["evidence"]["unique_destination_ports"] == count
            assert alert["evidence"]["syn_packets"] == packet_count
        else:
            assert alert["evidence"]["packets"] == packet_count


@pytest.mark.parametrize("config", [
    DetectionConfig(port_scan_unique_ports=0),
    DetectionConfig(high_rate_packets=-1),
    DetectionConfig(port_scan_window_seconds=0.0),
    DetectionConfig(high_rate_window_seconds=-1.0),
    DetectionConfig(high_rate_window_seconds=float("nan")),
    DetectionConfig(port_scan_window_seconds=float("inf")),
])
def test_invalid_config_raises_clear_value_error(config: DetectionConfig) -> None:
    with pytest.raises(ValueError, match="Detection"):
        detect_anomalies(_packets(1), config)
