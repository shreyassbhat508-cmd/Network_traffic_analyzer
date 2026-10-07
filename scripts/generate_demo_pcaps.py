#!/usr/bin/env python3
"""Generate deterministic demo PCAP and PCAPNG fixtures for Network Traffic Analyzer.

Generated Files in samples/:
  1. normal_traffic.pcap
  2. normal_traffic.pcapng
  3. port_scan.pcap
  4. high_rate.pcap
  5. suspicious_traffic.pcap
"""

import os
import sys
from typing import List

from scapy.all import (
    DNS,
    DNSQR,
    DNSRR,
    ICMP,
    IP,
    UDP,
    TCP,
    Raw,
    Packet,
    wrpcap,
)

BASE_TIME: float = 1700000000.0  # Deterministic epoch timestamp (2023-11-14 22:13:20 UTC)


def generate_normal_packets() -> List[Packet]:
    """Generate realistic mixed benign traffic (TCP, UDP, DNS, ICMP).

    Produces ZERO anomaly alerts with project detection rules.
    """
    packets: List[Packet] = []
    t = BASE_TIME

    # 1. DNS Query & Response 1 (example.com)
    dns_q1 = (
        IP(src="192.168.1.100", dst="8.8.8.8")
        / UDP(sport=53421, dport=53)
        / DNS(rd=1, qd=DNSQR(qname="example.com"))
    )
    dns_q1.time = t
    packets.append(dns_q1)

    t += 0.05
    dns_r1 = (
        IP(src="8.8.8.8", dst="192.168.1.100")
        / UDP(sport=53, dport=53421)
        / DNS(qr=1, rd=1, ra=1, qd=DNSQR(qname="example.com"), an=DNSRR(rrname="example.com", rdata="93.184.216.34"))
    )
    dns_r1.time = t
    packets.append(dns_r1)

    # 2. DNS Query & Response 2 (api.github.com)
    t += 0.2
    dns_q2 = (
        IP(src="192.168.1.101", dst="1.1.1.1")
        / UDP(sport=53422, dport=53)
        / DNS(rd=1, qd=DNSQR(qname="api.github.com"))
    )
    dns_q2.time = t
    packets.append(dns_q2)

    t += 0.05
    dns_r2 = (
        IP(src="1.1.1.1", dst="192.168.1.101")
        / UDP(sport=53, dport=53422)
        / DNS(qr=1, rd=1, ra=1, qd=DNSQR(qname="api.github.com"), an=DNSRR(rrname="api.github.com", rdata="140.82.121.4"))
    )
    dns_r2.time = t
    packets.append(dns_r2)

    # 3. HTTP TCP Conversation (192.168.1.100 -> 93.184.216.34:80)
    t += 0.5
    tcp_syn1 = (
        IP(src="192.168.1.100", dst="93.184.216.34")
        / TCP(sport=49152, dport=80, flags="S", seq=1000)
    )
    tcp_syn1.time = t
    packets.append(tcp_syn1)

    t += 0.03
    tcp_synack1 = (
        IP(src="93.184.216.34", dst="192.168.1.100")
        / TCP(sport=80, dport=49152, flags="SA", seq=5000, ack=1001)
    )
    tcp_synack1.time = t
    packets.append(tcp_synack1)

    t += 0.02
    tcp_ack1 = (
        IP(src="192.168.1.100", dst="93.184.216.34")
        / TCP(sport=49152, dport=80, flags="A", seq=1001, ack=5001)
    )
    tcp_ack1.time = t
    packets.append(tcp_ack1)

    t += 0.1
    http_get = (
        IP(src="192.168.1.100", dst="93.184.216.34")
        / TCP(sport=49152, dport=80, flags="PA", seq=1001, ack=5001)
        / Raw(b"GET / HTTP/1.1\r\nHost: example.com\r\n\r\n")
    )
    http_get.time = t
    packets.append(http_get)

    t += 0.05
    http_resp = (
        IP(src="93.184.216.34", dst="192.168.1.100")
        / TCP(sport=80, dport=49152, flags="PA", seq=5001, ack=1045)
        / Raw(b"HTTP/1.1 200 OK\r\nContent-Length: 13\r\n\r\nHello, World!")
    )
    http_resp.time = t
    packets.append(http_resp)

    t += 0.02
    tcp_fin1 = (
        IP(src="192.168.1.100", dst="93.184.216.34")
        / TCP(sport=49152, dport=80, flags="FA", seq=1045, ack=5058)
    )
    tcp_fin1.time = t
    packets.append(tcp_fin1)

    t += 0.02
    tcp_finack1 = (
        IP(src="93.184.216.34", dst="192.168.1.100")
        / TCP(sport=80, dport=49152, flags="FA", seq=5058, ack=1046)
    )
    tcp_finack1.time = t
    packets.append(tcp_finack1)

    # 4. HTTPS TCP Handshake & Data (192.168.1.102 -> 140.82.121.4:443)
    t += 0.4
    tcp_syn2 = (
        IP(src="192.168.1.102", dst="140.82.121.4")
        / TCP(sport=51234, dport=443, flags="S", seq=2000)
    )
    tcp_syn2.time = t
    packets.append(tcp_syn2)

    t += 0.04
    tcp_synack2 = (
        IP(src="140.82.121.4", dst="192.168.1.102")
        / TCP(sport=443, dport=51234, flags="SA", seq=7000, ack=2001)
    )
    tcp_synack2.time = t
    packets.append(tcp_synack2)

    t += 0.02
    tcp_ack2 = (
        IP(src="192.168.1.102", dst="140.82.121.4")
        / TCP(sport=51234, dport=443, flags="A", seq=2001, ack=7001)
    )
    tcp_ack2.time = t
    packets.append(tcp_ack2)

    t += 0.1
    tls_data = (
        IP(src="192.168.1.102", dst="140.82.121.4")
        / TCP(sport=51234, dport=443, flags="PA", seq=2001, ack=7001)
        / Raw(b"\x16\x03\x01\x00\x80ClientHelloPayloadData")
    )
    tls_data.time = t
    packets.append(tls_data)

    # 5. ICMP Ping Requests & Replies
    for i in range(2):
        t += 0.5
        icmp_req = (
            IP(src="192.168.1.100", dst="192.168.1.1")
            / ICMP(type=8, code=0, id=100, seq=i + 1)
            / Raw(b"PingPayloadData")
        )
        icmp_req.time = t
        packets.append(icmp_req)

        t += 0.01
        icmp_reply = (
            IP(src="192.168.1.1", dst="192.168.1.100")
            / ICMP(type=0, code=0, id=100, seq=i + 1)
            / Raw(b"PingPayloadData")
        )
        icmp_reply.time = t
        packets.append(icmp_reply)

    for i in range(2):
        t += 0.5
        icmp_req2 = (
            IP(src="192.168.1.105", dst="8.8.8.8")
            / ICMP(type=8, code=0, id=200, seq=i + 1)
            / Raw(b"PingGooglePayload")
        )
        icmp_req2.time = t
        packets.append(icmp_req2)

        t += 0.03
        icmp_reply2 = (
            IP(src="8.8.8.8", dst="192.168.1.105")
            / ICMP(type=0, code=0, id=200, seq=i + 1)
            / Raw(b"PingGooglePayload")
        )
        icmp_reply2.time = t
        packets.append(icmp_reply2)

    # 6. NTP Traffic over UDP
    t += 0.5
    ntp_req = (
        IP(src="192.168.1.100", dst="162.159.200.1")
        / UDP(sport=123, dport=123)
        / Raw(b"\x23\x00\x00\x00" + b"\x00" * 44)
    )
    ntp_req.time = t
    packets.append(ntp_req)

    t += 0.04
    ntp_resp = (
        IP(src="162.159.200.1", dst="192.168.1.100")
        / UDP(sport=123, dport=123)
        / Raw(b"\x24\x01\x00\x00" + b"\x00" * 44)
    )
    ntp_resp.time = t
    packets.append(ntp_resp)

    return packets


def generate_port_scan_packets() -> List[Packet]:
    """Generate TCP SYN port scan packets targeting 120 unique destination ports.

    Source: 10.0.0.50
    Destination: 10.0.0.10
    Ports: 1 through 120 (inclusive)
    Flags: SYN ('S'), ACK not set
    Window: < 60 seconds (0.2s interval -> 23.8 seconds total span)
    Total packets: 120
    """
    packets: List[Packet] = []
    t = BASE_TIME
    interval = 0.2  # 119 * 0.2 = 23.8 seconds <= 60 seconds

    for port in range(1, 121):
        pkt = (
            IP(src="10.0.0.50", dst="10.0.0.10")
            / TCP(sport=54321, dport=port, flags="S", seq=1000 + port)
        )
        pkt.time = t
        packets.append(pkt)
        t += interval

    return packets


def generate_high_rate_packets() -> List[Packet]:
    """Generate high-rate packet surge.

    Source: 10.0.0.60
    Destination: 10.0.0.20
    Count: exactly 350 packets
    Window: < 10 seconds (0.02s interval -> 6.98 seconds total span)
    Protocol: UDP
    Total packets: 350
    """
    packets: List[Packet] = []
    t = BASE_TIME
    interval = 0.02  # 349 * 0.02 = 6.98 seconds <= 10 seconds

    for i in range(350):
        pkt = (
            IP(src="10.0.0.60", dst="10.0.0.20")
            / UDP(sport=40000 + (i % 1000), dport=8080)
            / Raw(b"HIGH_RATE_BURST_DATA_PACKET_" + bytes(str(i), "ascii"))
        )
        pkt.time = t
        packets.append(pkt)
        t += interval

    return packets


def generate_suspicious_packets() -> List[Packet]:
    """Generate combined suspicious traffic containing both port scan and high rate patterns."""
    scan_pkts = generate_port_scan_packets()
    rate_pkts = generate_high_rate_packets()

    # Shift high rate pattern start time slightly to interleave naturally
    shift = 2.0
    for pkt in rate_pkts:
        pkt.time += shift

    combined = scan_pkts + rate_pkts
    combined.sort(key=lambda p: float(p.time))
    return combined


def main() -> None:
    output_dir = "samples"
    os.makedirs(output_dir, exist_ok=True)

    fixtures = {
        "normal_traffic.pcap": generate_normal_packets(),
        "normal_traffic.pcapng": generate_normal_packets(),
        "port_scan.pcap": generate_port_scan_packets(),
        "high_rate.pcap": generate_high_rate_packets(),
        "suspicious_traffic.pcap": generate_suspicious_packets(),
    }

    print("Generating demo PCAP/PCAPNG fixtures under samples/...")
    for filename, pkts in fixtures.items():
        filepath = os.path.join(output_dir, filename)
        wrpcap(filepath, pkts)
        print(f"  Created: {filepath} ({len(pkts)} packets)")

    print("\nGeneration complete.")


if __name__ == "__main__":
    main()
