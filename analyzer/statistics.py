"""Network statistics module for Network Traffic Analyzer.

Provides functionality to compute traffic metrics, protocol distribution,
top talkers (sources and destinations), packet size statistics, and a timeline.
"""

from __future__ import annotations

import pandas as pd

ORDERED_PROTOCOLS = ["TCP", "UDP", "ICMP", "DNS", "OTHER"]


def calculate_statistics(
    packets: pd.DataFrame, *, top_n: int = 10
) -> dict[str, object]:
    """Calculate aggregate network statistics from a packets DataFrame.

    Parameters
    ----------
    packets : pd.DataFrame
        Canonical DataFrame containing parsed packet rows.
    top_n : int, default 10
        Maximum number of top sources/destinations to return.

    Returns
    -------
    dict[str, object]
        Structured metrics dictionary complying with the shared statistics contract.
    """
    total_packets = len(packets) if packets is not None else 0

    if total_packets == 0 or packets.empty:
        return {
            "summary": {
                "total_packets": 0,
                "total_bytes": 0,
                "average_packet_size": 0.0,
                "min_packet_size": 0,
                "max_packet_size": 0,
                "unique_sources": 0,
                "unique_destinations": 0,
            },
            "protocol_distribution": [
                {"protocol": proto, "packets": 0, "percent": 0.0}
                for proto in ORDERED_PROTOCOLS
            ],
            "top_sources": [],
            "top_destinations": [],
            "packet_sizes": {
                "min": 0,
                "max": 0,
                "mean": 0.0,
                "median": 0.0,
                "p95": 0.0,
            },
            "timeline": [],
        }

    # Summary and Packet Sizes
    lengths = packets["length"] if "length" in packets else pd.Series([0] * total_packets)
    total_bytes = int(lengths.sum())
    min_size = int(lengths.min())
    max_size = int(lengths.max())
    mean_size = float(lengths.mean())
    median_size = float(lengths.median())
    p95_size = float(lengths.quantile(0.95))

    unique_sources = (
        int(packets["src_ip"].dropna().nunique())
        if "src_ip" in packets
        else 0
    )
    unique_destinations = (
        int(packets["dst_ip"].dropna().nunique())
        if "dst_ip" in packets
        else 0
    )

    summary: dict[str, object] = {
        "total_packets": total_packets,
        "total_bytes": total_bytes,
        "average_packet_size": mean_size,
        "min_packet_size": min_size,
        "max_packet_size": max_size,
        "unique_sources": unique_sources,
        "unique_destinations": unique_destinations,
    }

    packet_sizes: dict[str, object] = {
        "min": min_size,
        "max": max_size,
        "mean": mean_size,
        "median": median_size,
        "p95": p95_size,
    }

    # Protocol Distribution: strictly TCP, UDP, ICMP, DNS, OTHER
    proto_series = packets["protocol"] if "protocol" in packets else pd.Series([], dtype="object")
    proto_counts = proto_series.value_counts()

    protocol_distribution: list[dict[str, object]] = []
    for proto in ORDERED_PROTOCOLS:
        if proto == "OTHER":
            # Any protocol value not in the top 4 is included under OTHER
            other_cnt = sum(
                int(cnt)
                for p_name, cnt in proto_counts.items()
                if p_name not in ["TCP", "UDP", "ICMP", "DNS"]
            )
            count = other_cnt
        else:
            count = int(proto_counts.get(proto, 0))

        percent = float((count / total_packets) * 100.0)
        protocol_distribution.append(
            {"protocol": proto, "packets": count, "percent": percent}
        )

    # Top Sources
    top_sources: list[dict[str, object]] = []
    if "src_ip" in packets:
        src_valid = packets.dropna(subset=["src_ip"])
        if not src_valid.empty:
            src_grouped = (
                src_valid.groupby("src_ip", as_index=False)
                .agg(packets=("length", "count"), bytes=("length", "sum"))
                .sort_values(by=["packets", "bytes"], ascending=[False, False])
                .head(top_n)
            )
            top_sources = [
                {
                    "ip": str(row["src_ip"]),
                    "packets": int(row["packets"]),
                    "bytes": int(row["bytes"]),
                }
                for _, row in src_grouped.iterrows()
            ]

    # Top Destinations
    top_destinations: list[dict[str, object]] = []
    if "dst_ip" in packets:
        dst_valid = packets.dropna(subset=["dst_ip"])
        if not dst_valid.empty:
            dst_grouped = (
                dst_valid.groupby("dst_ip", as_index=False)
                .agg(packets=("length", "count"), bytes=("length", "sum"))
                .sort_values(by=["packets", "bytes"], ascending=[False, False])
                .head(top_n)
            )
            top_destinations = [
                {
                    "ip": str(row["dst_ip"]),
                    "packets": int(row["packets"]),
                    "bytes": int(row["bytes"]),
                }
                for _, row in dst_grouped.iterrows()
            ]

    # Timeline (1-second intervals, ISO8601 UTC formatted strings)
    timeline: list[dict[str, object]] = []
    if "timestamp" in packets:
        valid_ts = packets.dropna(subset=["timestamp"]).copy()
        if not valid_ts.empty:
            valid_ts["bucket"] = valid_ts["timestamp"].dt.floor("1s")
            timeline_grouped = (
                valid_ts.groupby("bucket", as_index=False)
                .agg(packets=("length", "count"), bytes=("length", "sum"))
                .sort_values("bucket")
            )
            timeline = [
                {
                    "timestamp": row["bucket"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "packets": int(row["packets"]),
                    "bytes": int(row["bytes"]),
                }
                for _, row in timeline_grouped.iterrows()
            ]

    return {
        "summary": summary,
        "protocol_distribution": protocol_distribution,
        "top_sources": top_sources,
        "top_destinations": top_destinations,
        "packet_sizes": packet_sizes,
        "timeline": timeline,
    }
