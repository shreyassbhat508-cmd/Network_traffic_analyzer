#!/usr/bin/env python3
"""Validation script for generated demo PCAP/PCAPNG fixtures."""

import os
import sys
from typing import Dict, List, Set, Tuple

from scapy.all import IP, TCP, UDP, ICMP, DNS, rdpcap, Packet


REQUIRED_FILES = [
    "samples/normal_traffic.pcap",
    "samples/normal_traffic.pcapng",
    "samples/port_scan.pcap",
    "samples/high_rate.pcap",
    "samples/suspicious_traffic.pcap",
]


def validate_fixtures() -> None:
    print("=" * 65)
    print("DEMO PCAP FIXTURE VALIDATION REPORT")
    print("=" * 65)

    # 1. Existence Check
    all_exist = True
    for filepath in REQUIRED_FILES:
        exists = os.path.isfile(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status = "EXISTS" if exists else "MISSING"
        print(f"[{status:7s}] {filepath:<35} Size: {size:>7d} bytes")
        if not exists:
            all_exist = False

    if not all_exist:
        print("\nERROR: Not all required fixture files exist under samples/")
        sys.exit(1)

    print("-" * 65)

    # 2. Scapy Parsing & Packet Counts Verification
    # Normal Traffic (.pcap and .pcapng)
    for nf in ["samples/normal_traffic.pcap", "samples/normal_traffic.pcapng"]:
        pkts: List[Packet] = rdpcap(nf)
        protocols: Set[str] = set()
        for p in pkts:
            if TCP in p:
                protocols.add("TCP")
                if DNS in p:
                    protocols.add("DNS")
            elif UDP in p:
                protocols.add("UDP")
                if DNS in p:
                    protocols.add("DNS")
            elif ICMP in p:
                protocols.add("ICMP")

        print(f"File: {nf}")
        print(f"  - Total Packets : {len(pkts)} (Expected: 25)")
        print(f"  - Protocols     : {sorted(list(protocols))}")
        assert len(pkts) == 25, f"{nf} has invalid packet count {len(pkts)}"
        assert "TCP" in protocols and "UDP" in protocols and "DNS" in protocols and "ICMP" in protocols, \
            f"{nf} is missing expected protocols"

    print("-" * 65)

    # Port Scan
    ps_file = "samples/port_scan.pcap"
    ps_pkts: List[Packet] = rdpcap(ps_file)
    ps_srcs: Set[str] = {p[IP].src for p in ps_pkts if IP in p}
    ps_dsts: Set[str] = {p[IP].dst for p in ps_pkts if IP in p}
    ps_ports: Set[int] = {int(p[TCP].dport) for p in ps_pkts if TCP in p}
    ps_syn_only: bool = all((p[TCP].flags == "S") for p in ps_pkts if TCP in p)
    ps_duration: float = float(ps_pkts[-1].time - ps_pkts[0].time)

    print(f"File: {ps_file}")
    pkts_count = len(ps_pkts)
    print(f"  - Total Packets : {pkts_count} (Expected: 120)")
    print(f"  - Source IP     : {ps_srcs} (Expected: {{'10.0.0.50'}})")
    print(f"  - Destination IP: {ps_dsts} (Expected: {{'10.0.0.10'}})")
    print(f"  - Unique Ports  : {len(ps_ports)} (Expected: 120, Range: {min(ps_ports)}-{max(ps_ports)})")
    print(f"  - TCP Flags     : SYN set, ACK not set ({'PASSED' if ps_syn_only else 'FAILED'})")
    print(f"  - Duration      : {ps_duration:.2f}s (Expected: <= 60.0s)")

    assert pkts_count == 120, f"port_scan.pcap has invalid packet count {pkts_count}"
    assert ps_srcs == {"10.0.0.50"}, f"Invalid source IP {ps_srcs}"
    assert ps_dsts == {"10.0.0.10"}, f"Invalid destination IP {ps_dsts}"
    assert len(ps_ports) == 120 and min(ps_ports) == 1 and max(ps_ports) == 120, "Invalid unique ports range"
    assert ps_syn_only, "Not all TCP packets are SYN-only"
    assert ps_duration <= 60.0, f"Port scan duration {ps_duration} exceeds 60s"

    print("-" * 65)

    # High Rate
    hr_file = "samples/high_rate.pcap"
    hr_pkts: List[Packet] = rdpcap(hr_file)
    hr_srcs: Set[str] = {p[IP].src for p in hr_pkts if IP in p}
    hr_dsts: Set[str] = {p[IP].dst for p in hr_pkts if IP in p}
    hr_duration: float = float(hr_pkts[-1].time - hr_pkts[0].time)

    print(f"File: {hr_file}")
    print(f"  - Total Packets : {len(hr_pkts)} (Expected: 350)")
    print(f"  - Source IP     : {hr_srcs} (Expected: {{'10.0.0.60'}})")
    print(f"  - Destination IP: {hr_dsts} (Expected: {{'10.0.0.20'}})")
    print(f"  - Duration      : {hr_duration:.2f}s (Expected: <= 10.0s)")

    assert len(hr_pkts) == 350, f"high_rate.pcap has invalid packet count {len(hr_pkts)}"
    assert hr_srcs == {"10.0.0.60"}, f"Invalid source IP {hr_srcs}"
    assert hr_dsts == {"10.0.0.20"}, f"Invalid destination IP {hr_dsts}"
    assert hr_duration <= 10.0, f"High rate duration {hr_duration} exceeds 10s"

    print("-" * 65)

    # Suspicious Traffic
    st_file = "samples/suspicious_traffic.pcap"
    st_pkts: List[Packet] = rdpcap(st_file)
    st_scan_pkts = [p for p in st_pkts if IP in p and p[IP].src == "10.0.0.50" and p[IP].dst == "10.0.0.10"]
    st_rate_pkts = [p for p in st_pkts if IP in p and p[IP].src == "10.0.0.60" and p[IP].dst == "10.0.0.20"]

    st_scan_ports: Set[int] = {int(p[TCP].dport) for p in st_scan_pkts if TCP in p}
    st_scan_duration: float = float(st_scan_pkts[-1].time - st_scan_pkts[0].time) if st_scan_pkts else 0.0
    st_rate_duration: float = float(st_rate_pkts[-1].time - st_rate_pkts[0].time) if st_rate_pkts else 0.0

    print(f"File: {st_file}")
    print(f"  - Total Packets : {len(st_pkts)} (Expected: 470)")
    print(f"  - Pattern 1 (Port Scan): {len(st_scan_pkts)} pkts | {len(st_scan_ports)} unique ports | {st_scan_duration:.2f}s")
    print(f"  - Pattern 2 (High Rate): {len(st_rate_pkts)} pkts | {st_rate_duration:.2f}s")

    assert len(st_pkts) == 470, f"suspicious_traffic.pcap has invalid packet count {len(st_pkts)}"
    assert len(st_scan_pkts) == 120 and len(st_scan_ports) == 120, "Suspicious traffic missing port scan pattern"
    assert len(st_rate_pkts) == 350, "Suspicious traffic missing high rate pattern"

    print("=" * 65)
    print("SUCCESS: ALL 10 FIXTURE VALIDATION CHECKS PASSED PERFECTLY!")
    print("=" * 65)


if __name__ == "__main__":
    validate_fixtures()
