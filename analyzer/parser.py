"""Packet parser module for Network Traffic Analyzer.

Provides functionality to incrementally parse PCAP and PCAPNG byte streams
into canonical pandas DataFrames and capture metadata.
"""

from __future__ import annotations

import io
import struct
from typing import Any

import pandas as pd
from scapy.error import Scapy_Exception
from scapy.layers.dns import DNS
from scapy.layers.inet import ICMP, IP, TCP, UDP
import scapy.layers.inet6 as inet6
from scapy.utils import PcapNgReader, PcapReader

CANONICAL_COLUMNS = [
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


def _build_empty_dataframe() -> pd.DataFrame:
    """Return an empty DataFrame matching the canonical contract and dtypes."""
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


def _detect_format(data: bytes, reader: Any = None) -> str:
    """Detect capture file format: PCAP, PCAPNG, or UNKNOWN."""
    if len(data) >= 4:
        magic4 = bytes(data[:4])
        if magic4 == b"\x0a\x0d\x0d\x0a":
            return "PCAPNG"
        if magic4 in (
            b"\xa1\xb2\xc3\xd4",
            b"\xd4\xc3\xb2\xa1",
            b"\xa1\xb2\x3c\x4d",
            b"\x4d\x3c\xb2\xa1",
        ):
            return "PCAP"
        if data[:2] == b"\x1f\x8b":
            try:
                import gzip

                decompressed = gzip.decompress(data[:64])
                if decompressed.startswith(b"\x0a\x0d\x0d\x0a"):
                    return "PCAPNG"
                if any(
                    decompressed.startswith(m)
                    for m in (
                        b"\xa1\xb2\xc3\xd4",
                        b"\xd4\xc3\xb2\xa1",
                        b"\xa1\xb2\x3c\x4d",
                        b"\x4d\x3c\xb2\xa1",
                    )
                ):
                    return "PCAP"
            except Exception:
                pass

    if reader is not None:
        if isinstance(reader, PcapNgReader):
            return "PCAPNG"
        if isinstance(reader, PcapReader):
            return "PCAP"

    return "UNKNOWN"


def _is_icmp(pkt: Any) -> bool:
    """Check if packet contains ICMP or ICMPv6."""
    if pkt.haslayer(ICMP):
        return True
    try:
        for layer_cls in pkt.layers():
            if issubclass(layer_cls, inet6._ICMPv6) or layer_cls.__name__.startswith("ICMPv6"):
                return True
    except Exception:
        pass
    return False


def _extract_dns(pkt: Any) -> tuple[bool, str | None]:
    """Check if packet contains DNS and extract query string if present."""
    if not pkt.haslayer(DNS):
        return False, None
    dns_layer = pkt[DNS]
    dns_query: str | None = None
    qd = getattr(dns_layer, "qd", None)
    first_qr = None
    if qd is not None:
        if hasattr(qd, "__getitem__") and hasattr(qd, "__len__"):
            try:
                first_qr = qd[0] if len(qd) > 0 else None
            except Exception:
                first_qr = qd
        else:
            first_qr = qd

    if first_qr is not None:
        qname = getattr(first_qr, "qname", None)
        if qname is not None:
            if isinstance(qname, bytes):
                decoded = qname.decode("utf-8", errors="replace").rstrip(".")
                dns_query = decoded if decoded else "."
            elif isinstance(qname, str):
                cleaned = qname.rstrip(".")
                dns_query = cleaned if cleaned else "."
    return True, dns_query


def parse_capture_bytes(
    data: bytes, filename: str, *, max_packets: int = 100_000
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Parse raw capture bytes into a canonical DataFrame and metadata.

    Parameters
    ----------
    data : bytes
        The raw PCAP or PCAPNG file content.
    filename : str
        Name of the capture file being parsed.
    max_packets : int, default 100_000
        Maximum number of packets to parse before truncating.

    Returns
    -------
    tuple[pd.DataFrame, dict[str, object]]
        Tuple containing the canonical packet DataFrame and the metadata dictionary.

    Raises
    ------
    ValueError
        If the file content is corrupted or unsupported.
    """
    if not isinstance(data, (bytes, bytearray)):
        raise ValueError(f"Invalid input data type for '{filename}': expected bytes.")

    file_size_bytes = len(data)

    if file_size_bytes == 0:
        metadata: dict[str, object] = {
            "filename": filename,
            "file_size_bytes": 0,
            "format": "UNKNOWN",
            "parsed_packets": 0,
            "truncated": False,
            "warnings": ["Empty capture data."],
        }
        return _build_empty_dataframe(), metadata

    detected_format = _detect_format(data)
    bio = io.BytesIO(data)

    try:
        reader = PcapReader(bio)
    except (Scapy_Exception, struct.error, EOFError, OSError) as err:
        raise ValueError(
            f"Corrupt or unsupported capture file '{filename}': {err}"
        ) from err
    except Exception as err:
        raise ValueError(
            f"Unexpected error reading capture file '{filename}': {err}"
        ) from err

    if detected_format == "UNKNOWN":
        detected_format = _detect_format(data, reader)

    timestamps: list[float] = []
    src_ips: list[str | None] = []
    dst_ips: list[str | None] = []
    src_ports: list[int | None] = []
    dst_ports: list[int | None] = []
    protocols: list[str] = []
    transports: list[str | None] = []
    lengths: list[int] = []
    tcp_flags_list: list[str | None] = []
    ip_versions: list[int | None] = []
    dns_queries: list[str | None] = []

    parsed_packets = 0
    truncated = False
    warnings: list[str] = []

    try:
        for pkt in reader:
            if parsed_packets >= max_packets:
                truncated = True
                warnings.append(
                    f"Capture truncated at max_packets limit of {max_packets}."
                )
                break

            # Packet length
            pkt_len = int(len(pkt))
            lengths.append(pkt_len)

            # Timestamp
            raw_time = getattr(pkt, "time", None)
            timestamps.append(float(raw_time) if raw_time is not None else 0.0)

            # IP Layer
            if pkt.haslayer(IP):
                src_ips.append(str(pkt[IP].src))
                dst_ips.append(str(pkt[IP].dst))
                ip_versions.append(4)
            elif pkt.haslayer(inet6.IPv6):
                src_ips.append(str(pkt[inet6.IPv6].src))
                dst_ips.append(str(pkt[inet6.IPv6].dst))
                ip_versions.append(6)
            else:
                src_ips.append(None)
                dst_ips.append(None)
                ip_versions.append(None)

            # L4 Transport (TCP vs UDP)
            has_tcp = pkt.haslayer(TCP)
            has_udp = pkt.haslayer(UDP)
            if has_tcp:
                tcp_layer = pkt[TCP]
                src_ports.append(int(tcp_layer.sport))
                dst_ports.append(int(tcp_layer.dport))
                transports.append("TCP")
                tcp_flags_list.append(str(tcp_layer.flags))
            elif has_udp:
                udp_layer = pkt[UDP]
                src_ports.append(int(udp_layer.sport))
                dst_ports.append(int(udp_layer.dport))
                transports.append("UDP")
                tcp_flags_list.append(None)
            else:
                src_ports.append(None)
                dst_ports.append(None)
                transports.append(None)
                tcp_flags_list.append(None)

            # DNS & Protocol classification
            has_dns, dns_query = _extract_dns(pkt)
            dns_queries.append(dns_query)

            if has_dns:
                protocols.append("DNS")
            elif has_tcp:
                protocols.append("TCP")
            elif has_udp:
                protocols.append("UDP")
            elif _is_icmp(pkt):
                protocols.append("ICMP")
            else:
                protocols.append("OTHER")

            parsed_packets += 1

    except (Scapy_Exception, struct.error, EOFError) as err:
        if parsed_packets == 0:
            raise ValueError(
                f"Corrupt capture file '{filename}': {err}"
            ) from err
        # Mid-stream corruption warning if some packets were already read
        warnings.append(f"Corrupt packet stream encountered after {parsed_packets} packets: {err}")
    finally:
        try:
            reader.close()
        except Exception:
            pass

    if parsed_packets == 0:
        df = _build_empty_dataframe()
    else:
        ts_series = pd.to_datetime(timestamps, unit="s", utc=True).astype(
            "datetime64[ns, UTC]"
        )
        df = pd.DataFrame(
            {
                "timestamp": ts_series,
                "src_ip": pd.Series(src_ips, dtype="object"),
                "dst_ip": pd.Series(dst_ips, dtype="object"),
                "src_port": pd.Series(src_ports, dtype="Int64"),
                "dst_port": pd.Series(dst_ports, dtype="Int64"),
                "protocol": pd.Series(protocols, dtype="object"),
                "transport": pd.Series(transports, dtype="object"),
                "length": pd.Series(lengths, dtype="int64"),
                "tcp_flags": pd.Series(tcp_flags_list, dtype="object"),
                "ip_version": pd.Series(ip_versions, dtype="Int64"),
                "dns_query": pd.Series(dns_queries, dtype="object"),
            }
        )

    metadata = {
        "filename": filename,
        "file_size_bytes": file_size_bytes,
        "format": detected_format,
        "parsed_packets": parsed_packets,
        "truncated": truncated,
        "warnings": warnings,
    }

    return df, metadata
