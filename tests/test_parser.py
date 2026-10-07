"""Unit tests for the packet parser module."""

from __future__ import annotations

import io
import os
from pathlib import Path
import struct
import sys
import tempfile

# Ensure workspace root is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import pytest
from scapy.layers.dns import DNS, DNSQR
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.inet6 import IPv6, ICMPv6EchoRequest
from scapy.layers.l2 import ARP, Ether
from scapy.packet import Packet
from scapy.utils import PcapNgWriter, PcapWriter

from analyzer.parser import CANONICAL_COLUMNS, parse_capture_bytes

ETH_KWARGS = {"src": "00:11:22:33:44:55", "dst": "66:77:88:99:aa:bb"}


def make_pcap_bytes(packets: list[Packet]) -> bytes:
    """Helper to serialize a list of Scapy packets to in-memory PCAP bytes."""
    bio = io.BytesIO()
    writer = PcapWriter(bio)
    for pkt in packets:
        writer.write(pkt)
    writer.flush()
    return bio.getvalue()


def make_pcapng_bytes(packets: list[Packet]) -> bytes:
    """Helper to serialize a list of Scapy packets to in-memory PCAPNG bytes."""
    with tempfile.NamedTemporaryFile(suffix=".pcapng", delete=False) as tf:
        tf_name = tf.name
    try:
        writer = PcapNgWriter(tf_name)
        for pkt in packets:
            writer.write(pkt)
        writer.close()
        with open(tf_name, "rb") as f:
            return f.read()
    finally:
        if os.path.exists(tf_name):
            os.remove(tf_name)


def test_canonical_dataframe_columns_and_dtypes_populated():
    pkt = Ether(**ETH_KWARGS) / IP(src="1.1.1.1", dst="2.2.2.2") / TCP(sport=80, dport=443, flags="S")
    pcap_data = make_pcap_bytes([pkt])

    df, meta = parse_capture_bytes(pcap_data, "test.pcap")

    assert list(df.columns) == CANONICAL_COLUMNS
    assert df["timestamp"].dtype == "datetime64[ns, UTC]"
    assert df["src_ip"].dtype == "object"
    assert df["dst_ip"].dtype == "object"
    assert df["src_port"].dtype == "Int64"
    assert df["dst_port"].dtype == "Int64"
    assert df["protocol"].dtype == "object"
    assert df["transport"].dtype == "object"
    assert df["length"].dtype == "int64"
    assert df["tcp_flags"].dtype == "object"
    assert df["ip_version"].dtype == "Int64"
    assert df["dns_query"].dtype == "object"


def test_canonical_dataframe_columns_and_dtypes_empty():
    df, meta = parse_capture_bytes(b"", "empty.pcap")

    assert list(df.columns) == CANONICAL_COLUMNS
    assert df["timestamp"].dtype == "datetime64[ns, UTC]"
    assert df["src_ip"].dtype == "object"
    assert df["dst_ip"].dtype == "object"
    assert df["src_port"].dtype == "Int64"
    assert df["dst_port"].dtype == "Int64"
    assert df["protocol"].dtype == "object"
    assert df["transport"].dtype == "object"
    assert df["length"].dtype == "int64"
    assert df["tcp_flags"].dtype == "object"
    assert df["ip_version"].dtype == "Int64"
    assert df["dns_query"].dtype == "object"
    assert len(df) == 0


def test_parse_pcap():
    pkt = Ether(**ETH_KWARGS) / IP(src="10.0.0.1", dst="10.0.0.2") / TCP(sport=1234, dport=80)
    data = make_pcap_bytes([pkt])

    df, meta = parse_capture_bytes(data, "traffic.pcap")

    assert meta["filename"] == "traffic.pcap"
    assert meta["file_size_bytes"] == len(data)
    assert meta["format"] == "PCAP"
    assert meta["parsed_packets"] == 1
    assert meta["truncated"] is False
    assert meta["warnings"] == []
    assert len(df) == 1


def test_parse_pcapng():
    pkt = Ether(**ETH_KWARGS) / IP(src="10.0.0.1", dst="10.0.0.2") / UDP(sport=5000, dport=6000)
    data = make_pcapng_bytes([pkt])

    df, meta = parse_capture_bytes(data, "traffic.pcapng")

    assert meta["filename"] == "traffic.pcapng"
    assert meta["file_size_bytes"] == len(data)
    assert meta["format"] == "PCAPNG"
    assert meta["parsed_packets"] == 1
    assert meta["truncated"] is False
    assert meta["warnings"] == []
    assert len(df) == 1


def test_ipv4_packet_parsing():
    pkt = Ether(**ETH_KWARGS) / IP(src="172.16.0.5", dst="172.16.0.10") / TCP(sport=8080, dport=9090)
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "ipv4.pcap")

    assert df.loc[0, "src_ip"] == "172.16.0.5"
    assert df.loc[0, "dst_ip"] == "172.16.0.10"
    assert df.loc[0, "ip_version"] == 4


def test_ipv6_packet_parsing():
    pkt = Ether(**ETH_KWARGS) / IPv6(src="2001:db8::10", dst="2001:db8::20") / UDP(sport=3000, dport=4000)
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "ipv6.pcap")

    assert df.loc[0, "src_ip"] == "2001:db8::10"
    assert df.loc[0, "dst_ip"] == "2001:db8::20"
    assert df.loc[0, "ip_version"] == 6


def test_tcp_packet_parsing():
    pkt = Ether(**ETH_KWARGS) / IP(src="192.168.1.1", dst="192.168.1.2") / TCP(sport=22, dport=54321, flags="SA")
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "tcp.pcap")

    assert df.loc[0, "protocol"] == "TCP"
    assert df.loc[0, "transport"] == "TCP"
    assert df.loc[0, "src_port"] == 22
    assert df.loc[0, "dst_port"] == 54321
    assert "S" in df.loc[0, "tcp_flags"] and "A" in df.loc[0, "tcp_flags"]
    assert df.loc[0, "dns_query"] is None


def test_udp_packet_parsing():
    pkt = Ether(**ETH_KWARGS) / IP(src="192.168.1.1", dst="192.168.1.2") / UDP(sport=123, dport=123)
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "udp.pcap")

    assert df.loc[0, "protocol"] == "UDP"
    assert df.loc[0, "transport"] == "UDP"
    assert df.loc[0, "src_port"] == 123
    assert df.loc[0, "dst_port"] == 123
    assert df.loc[0, "tcp_flags"] is None
    assert df.loc[0, "dns_query"] is None


def test_icmp_ipv4_parsing():
    pkt = Ether(**ETH_KWARGS) / IP(src="192.168.1.1", dst="192.168.1.2") / ICMP()
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "icmp.pcap")

    assert df.loc[0, "protocol"] == "ICMP"
    assert df.loc[0, "transport"] is None
    assert pd.isna(df.loc[0, "src_port"])
    assert pd.isna(df.loc[0, "dst_port"])
    assert df.loc[0, "tcp_flags"] is None


def test_icmpv6_parsing():
    pkt = Ether(**ETH_KWARGS) / IPv6(src="fe80::1", dst="fe80::2") / ICMPv6EchoRequest()
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "icmpv6.pcap")

    assert df.loc[0, "protocol"] == "ICMP"
    assert df.loc[0, "transport"] is None
    assert pd.isna(df.loc[0, "src_port"])
    assert pd.isna(df.loc[0, "dst_port"])
    assert df.loc[0, "ip_version"] == 6


def test_dns_over_udp_parsing():
    pkt = (
        Ether(**ETH_KWARGS)
        / IP(src="192.168.1.50", dst="8.8.8.8")
        / UDP(sport=53000, dport=53)
        / DNS(rd=1, qd=DNSQR(qname="openai.com"))
    )
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "dns_udp.pcap")

    assert df.loc[0, "protocol"] == "DNS"
    assert df.loc[0, "transport"] == "UDP"
    assert df.loc[0, "src_port"] == 53000
    assert df.loc[0, "dst_port"] == 53
    assert df.loc[0, "dns_query"] == "openai.com"


def test_dns_over_tcp_parsing():
    pkt = (
        Ether(**ETH_KWARGS)
        / IP(src="192.168.1.50", dst="1.1.1.1")
        / TCP(sport=54000, dport=53, flags="PA")
        / DNS(rd=1, qd=DNSQR(qname=b"github.com."))
    )
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "dns_tcp.pcap")

    assert df.loc[0, "protocol"] == "DNS"
    assert df.loc[0, "transport"] == "TCP"
    assert df.loc[0, "src_port"] == 54000
    assert df.loc[0, "dst_port"] == 53
    assert df.loc[0, "dns_query"] == "github.com"
    assert df.loc[0, "tcp_flags"] is not None


def test_non_ip_packet_parsing():
    pkt = Ether(**ETH_KWARGS) / ARP(psrc="192.168.1.1", pdst="192.168.1.2")
    data = make_pcap_bytes([pkt])

    df, _ = parse_capture_bytes(data, "arp.pcap")

    assert len(df) == 1
    assert df.loc[0, "src_ip"] is None
    assert df.loc[0, "dst_ip"] is None
    assert pd.isna(df.loc[0, "src_port"])
    assert pd.isna(df.loc[0, "dst_port"])
    assert pd.isna(df.loc[0, "ip_version"])
    assert df.loc[0, "protocol"] == "OTHER"
    assert df.loc[0, "transport"] is None
    assert df.loc[0, "tcp_flags"] is None
    assert df.loc[0, "dns_query"] is None


def test_empty_capture_data():
    df, meta = parse_capture_bytes(b"", "empty.pcap")

    assert len(df) == 0
    assert meta["file_size_bytes"] == 0
    assert meta["format"] == "UNKNOWN"
    assert meta["parsed_packets"] == 0
    assert meta["truncated"] is False
    assert len(meta["warnings"]) > 0


def test_empty_valid_pcap_file():
    # 24-byte PCAP header with 0 packet records
    hdr = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)
    df, meta = parse_capture_bytes(hdr, "zero_packets.pcap")

    assert len(df) == 0
    assert meta["file_size_bytes"] == 24
    assert meta["format"] == "PCAP"
    assert meta["parsed_packets"] == 0
    assert meta["truncated"] is False
    assert meta["warnings"] == []


def test_corrupt_input_raises_value_error():
    with pytest.raises(ValueError, match="Corrupt or unsupported"):
        parse_capture_bytes(b"This is completely invalid capture file content.", "corrupt.pcap")

    # Truncated PCAP magic / header
    with pytest.raises(ValueError, match="Corrupt or unsupported"):
        parse_capture_bytes(b"\xd4\xc3\xb2\xa1\x02\x00", "truncated_header.pcap")


def test_max_packets_truncation():
    packets = [
        Ether(**ETH_KWARGS) / IP(src=f"10.0.0.{i}", dst="10.0.0.1") / TCP(sport=1000 + i, dport=80)
        for i in range(10)
    ]
    data = make_pcap_bytes(packets)

    df, meta = parse_capture_bytes(data, "ten_packets.pcap", max_packets=4)

    assert len(df) == 4
    assert meta["parsed_packets"] == 4
    assert meta["truncated"] is True
    assert any("max_packets limit of 4" in w for w in meta["warnings"])
