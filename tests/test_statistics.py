"""Unit tests for network statistics module."""

from __future__ import annotations

import inspect
from pathlib import Path
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest

from analyzer.statistics import calculate_statistics


@pytest.fixture
def empty_packets_df() -> pd.DataFrame:
    """Fixture providing an empty canonical packets DataFrame."""
    return pd.DataFrame(
        {
            "timestamp": pd.Series([], dtype="datetime64[ns, UTC]"),
            "src_ip": pd.Series([], dtype="object"),
            "dst_ip": pd.Series([], dtype="object"),
            "src_port": pd.Series([], dtype="Int64"),
            "dst_port": pd.Series([], dtype="Int64"),
            "protocol": pd.Series([], dtype="object"),
            "transport": pd.Series([], dtype="object"),
            "length": pd.Series([], dtype="int64"),
            "tcp_flags": pd.Series([], dtype="object"),
            "ip_version": pd.Series([], dtype="Int64"),
            "dns_query": pd.Series([], dtype="object"),
        }
    )


@pytest.fixture
def sample_packets_df() -> pd.DataFrame:
    """Fixture providing a diverse set of packets for statistical assertions."""
    timestamps = [
        "2026-10-07T10:00:00.100Z",
        "2026-10-07T10:00:00.400Z",
        "2026-10-07T10:00:01.050Z",
        "2026-10-07T10:00:01.800Z",
        "2026-10-07T10:00:02.300Z",
    ]
    return pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps, utc=True).astype("datetime64[ns, UTC]"),
            "src_ip": pd.Series(["192.168.1.10", "192.168.1.10", "192.168.1.20", "192.168.1.30", None], dtype="object"),
            "dst_ip": pd.Series(["8.8.8.8", "8.8.8.8", "192.168.1.10", "1.1.1.1", None], dtype="object"),
            "src_port": pd.Series([53000, 53001, 80, 443, None], dtype="Int64"),
            "dst_port": pd.Series([53, 53, 54321, 54322, None], dtype="Int64"),
            "protocol": pd.Series(["DNS", "DNS", "TCP", "UDP", "OTHER"], dtype="object"),
            "transport": pd.Series(["UDP", "UDP", "TCP", "UDP", "OTHER"], dtype="object"),
            "length": pd.Series([100, 200, 300, 400, 50], dtype="int64"),
            "tcp_flags": pd.Series([None, None, "PA", None, None], dtype="object"),
            "ip_version": pd.Series([4, 4, 4, 4, None], dtype="Int64"),
            "dns_query": pd.Series(["google.com", "example.com", None, None, None], dtype="object"),
        }
    )


def test_empty_dataframe_statistics(empty_packets_df):
    stats = calculate_statistics(empty_packets_df)

    assert "summary" in stats
    assert "protocol_distribution" in stats
    assert "top_sources" in stats
    assert "top_destinations" in stats
    assert "packet_sizes" in stats
    assert "timeline" in stats

    summary = stats["summary"]
    assert summary["total_packets"] == 0
    assert summary["total_bytes"] == 0
    assert summary["average_packet_size"] == 0.0
    assert summary["min_packet_size"] == 0
    assert summary["max_packet_size"] == 0
    assert summary["unique_sources"] == 0
    assert summary["unique_destinations"] == 0

    proto_dist = stats["protocol_distribution"]
    assert len(proto_dist) == 5
    expected_order = ["TCP", "UDP", "ICMP", "DNS", "OTHER"]
    for i, proto_name in enumerate(expected_order):
        assert proto_dist[i]["protocol"] == proto_name
        assert proto_dist[i]["packets"] == 0
        assert proto_dist[i]["percent"] == 0.0

    assert stats["top_sources"] == []
    assert stats["top_destinations"] == []

    sizes = stats["packet_sizes"]
    assert sizes["min"] == 0
    assert sizes["max"] == 0
    assert sizes["mean"] == 0.0
    assert sizes["median"] == 0.0
    assert sizes["p95"] == 0.0

    assert stats["timeline"] == []


def test_summary_statistics(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    summary = stats["summary"]

    assert summary["total_packets"] == 5
    # 100 + 200 + 300 + 400 + 50 = 1050
    assert summary["total_bytes"] == 1050
    assert summary["average_packet_size"] == 210.0
    assert summary["min_packet_size"] == 50
    assert summary["max_packet_size"] == 400
    # Unique non-null sources: 192.168.1.10, 192.168.1.20, 192.168.1.30 -> 3
    assert summary["unique_sources"] == 3
    # Unique non-null destinations: 8.8.8.8, 192.168.1.10, 1.1.1.1 -> 3
    assert summary["unique_destinations"] == 3


def test_protocol_percentages_and_order(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    proto_dist = stats["protocol_distribution"]

    # Protocol order MUST follow: TCP, UDP, ICMP, DNS, OTHER
    order = [item["protocol"] for item in proto_dist]
    assert order == ["TCP", "UDP", "ICMP", "DNS", "OTHER"]

    by_proto = {item["protocol"]: item for item in proto_dist}
    # 5 packets total: 1 TCP (20%), 1 UDP (20%), 0 ICMP (0%), 2 DNS (40%), 1 OTHER (20%)
    assert by_proto["TCP"]["packets"] == 1
    assert pytest.approx(by_proto["TCP"]["percent"]) == 20.0

    assert by_proto["UDP"]["packets"] == 1
    assert pytest.approx(by_proto["UDP"]["percent"]) == 20.0

    assert by_proto["ICMP"]["packets"] == 0
    assert pytest.approx(by_proto["ICMP"]["percent"]) == 0.0

    assert by_proto["DNS"]["packets"] == 2
    assert pytest.approx(by_proto["DNS"]["percent"]) == 40.0

    assert by_proto["OTHER"]["packets"] == 1
    assert pytest.approx(by_proto["OTHER"]["percent"]) == 20.0

    total_pct = sum(item["percent"] for item in proto_dist)
    assert pytest.approx(total_pct) == 100.0


def test_top_sources_statistics(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    top_sources = stats["top_sources"]

    assert len(top_sources) == 3
    # 192.168.1.10 sent 2 packets (100 + 200 = 300 bytes)
    assert top_sources[0]["ip"] == "192.168.1.10"
    assert top_sources[0]["packets"] == 2
    assert top_sources[0]["bytes"] == 300

    # 192.168.1.30 sent 1 packet of 400 bytes, 192.168.1.20 sent 1 packet of 300 bytes
    # Sorted by packets descending, then bytes descending
    assert top_sources[1]["ip"] == "192.168.1.30"
    assert top_sources[1]["packets"] == 1
    assert top_sources[1]["bytes"] == 400

    assert top_sources[2]["ip"] == "192.168.1.20"
    assert top_sources[2]["packets"] == 1
    assert top_sources[2]["bytes"] == 300


def test_top_destinations_statistics(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    top_destinations = stats["top_destinations"]

    assert len(top_destinations) == 3
    # 8.8.8.8 received 2 packets (100 + 200 = 300 bytes)
    assert top_destinations[0]["ip"] == "8.8.8.8"
    assert top_destinations[0]["packets"] == 2
    assert top_destinations[0]["bytes"] == 300

    # 1.1.1.1 received 1 packet (400 bytes), 192.168.1.10 received 1 packet (300 bytes)
    assert top_destinations[1]["ip"] == "1.1.1.1"
    assert top_destinations[1]["packets"] == 1
    assert top_destinations[1]["bytes"] == 400

    assert top_destinations[2]["ip"] == "192.168.1.10"
    assert top_destinations[2]["packets"] == 1
    assert top_destinations[2]["bytes"] == 300


def test_packet_sizes_statistics(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    sizes = stats["packet_sizes"]

    # lengths: [50, 100, 200, 300, 400]
    assert sizes["min"] == 50
    assert sizes["max"] == 400
    assert pytest.approx(sizes["mean"]) == 210.0
    assert sizes["median"] == 200.0
    # quantile 0.95 of [50, 100, 200, 300, 400]
    expected_p95 = pd.Series([50, 100, 200, 300, 400]).quantile(0.95)
    assert pytest.approx(sizes["p95"]) == float(expected_p95)


def test_timeline_statistics(sample_packets_df):
    stats = calculate_statistics(sample_packets_df)
    timeline = stats["timeline"]

    # In sample_packets_df:
    # 10:00:00 has 2 packets (100 + 200 = 300 bytes)
    # 10:00:01 has 2 packets (300 + 400 = 700 bytes)
    # 10:00:02 has 1 packet (50 bytes)
    assert len(timeline) == 3

    assert timeline[0]["timestamp"] == "2026-10-07T10:00:00Z"
    assert timeline[0]["packets"] == 2
    assert timeline[0]["bytes"] == 300

    assert timeline[1]["timestamp"] == "2026-10-07T10:00:01Z"
    assert timeline[1]["packets"] == 2
    assert timeline[1]["bytes"] == 700

    assert timeline[2]["timestamp"] == "2026-10-07T10:00:02Z"
    assert timeline[2]["packets"] == 1
    assert timeline[2]["bytes"] == 50


def test_frozen_statistics_signature_and_keys(sample_packets_df, empty_packets_df):
    assert list(inspect.signature(calculate_statistics).parameters) == ["packets"]
    for packets in (sample_packets_df, empty_packets_df):
        stats = calculate_statistics(packets)
        assert set(stats["summary"]) == {
            "total_packets", "total_bytes", "average_packet_size", "min_packet_size",
            "max_packet_size", "unique_sources", "unique_destinations",
        }
        assert set(stats["packet_sizes"]) == {"min", "max", "mean", "median", "p95"}
        for talker in stats["top_sources"] + stats["top_destinations"]:
            assert set(talker) == {"ip", "packets", "bytes"}
            assert talker["ip"] is not None
        for bucket in stats["timeline"]:
            assert set(bucket) == {"timestamp", "packets", "bytes"}


@pytest.mark.parametrize("duration,bucket_seconds", [(120, 1), (121, 5), (1800, 5), (1801, 60)])
def test_timeline_bucket_duration_boundaries(sample_packets_df, duration, bucket_seconds):
    packets = sample_packets_df.iloc[[0, 1]].copy()
    start = pd.Timestamp("2026-10-07T10:00:01Z")
    end = start + pd.Timedelta(seconds=duration)
    packets["timestamp"] = pd.Series([start, end], index=packets.index, dtype="datetime64[ns, UTC]")
    timeline = calculate_statistics(packets)["timeline"]
    assert [bucket["timestamp"] for bucket in timeline] == [
        timestamp.floor(f"{bucket_seconds}s").strftime("%Y-%m-%dT%H:%M:%SZ")
        for timestamp in (start, end)
    ]
    assert sum(bucket["packets"] for bucket in timeline) == 2
    assert sum(bucket["bytes"] for bucket in timeline) == 300
