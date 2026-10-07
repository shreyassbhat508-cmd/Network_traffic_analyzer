"""Frozen shared contracts; changes require Savyl's approval."""

from dataclasses import dataclass
from typing import Final


PACKET_COLUMNS: Final[list[str]] = [
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

PROTOCOL_ORDER: Final[list[str]] = [
    "TCP",
    "UDP",
    "ICMP",
    "DNS",
    "OTHER",
]

MAX_FILE_BYTES: Final[int] = 25 * 1024 * 1024
MAX_PACKETS: Final[int] = 100_000


@dataclass(frozen=True)
class DetectionConfig:
    """Shared thresholds for future deterministic anomaly detection."""

    port_scan_unique_ports: int = 100
    port_scan_window_seconds: float = 60.0
    high_rate_packets: int = 300
    high_rate_window_seconds: float = 10.0
