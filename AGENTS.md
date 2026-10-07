# Network Traffic Analyzer with Packet Sniffing

This is a four-person university hackathon project. Savyl (Member A) owns
backend architecture, shared contracts, deterministic anomaly detection, service
orchestration, backend testing, cross-module integration, and final technical
integration.

## Team ownership

| Owner | Files and responsibilities |
| --- | --- |
| Savyl | `requirements.txt`, `.gitignore`, `AGENTS.md`, `analyzer/__init__.py`, `analyzer/contracts.py`, `analyzer/anomaly_detector.py`, `analyzer/service.py`, `tests/test_anomaly_detector.py`, `tests/test_service.py`, architecture/integration |
| Sudhit | `analyzer/parser.py`, `analyzer/statistics.py`, `tests/test_parser.py`, `tests/test_statistics.py` |
| Suhaan | `app.py`, `.streamlit/config.toml`, `ui/`, frontend/UI/manual UI testing |
| Shreyas | `README.md`, `scripts/generate_demo_pcaps.py`, `samples/`, `docs/`, `screenshots/`, demo/documentation material |

Respect ownership boundaries. Do not write implementation code in another
member's files or rewrite their implementation just because a different design
is preferred. Coordinate necessary changes with the owner. No unrelated refactors.
Keep interfaces backward-compatible during integration and prefer minimal
compatibility fixes over large rewrites.

Do not add dependencies without approval. The dependency pins are:
`scapy==2.8.0`, `pandas==3.0.6`, `streamlit==1.65.0`, `plotly==7.1.0`,
and `pytest==9.1.1`.

Savyl reviews and commits changes. Do not commit, push, merge, create branches,
or modify Git history unless Savyl explicitly authorizes a later change to this rule.

## Frozen shared contracts

`analyzer/contracts.py` must not be casually changed. Its constants and
`DetectionConfig` are shared interfaces. Other team members must not rename,
add, remove, reorder, or change the meaning/dtype of packet fields without
Savyl's approval. Treat the shared column lists as constants; do not mutate them.

`PACKET_COLUMNS` is frozen in exactly this order:

```python
PACKET_COLUMNS = [
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
PROTOCOL_ORDER = ["TCP", "UDP", "ICMP", "DNS", "OTHER"]
MAX_FILE_BYTES = 25 * 1024 * 1024
MAX_PACKETS = 100_000
```

The future parser returns one pandas DataFrame row per packet:

| Column | Frozen meaning/dtype |
| --- | --- |
| `timestamp` | Timezone-aware pandas `datetime64[ns, UTC]` |
| `src_ip` | IPv4/IPv6 source string; `None` for non-IP packets |
| `dst_ip` | IPv4/IPv6 destination string; `None` for non-IP packets |
| `src_port` | pandas nullable `Int64`; TCP/UDP source port, otherwise `pd.NA` |
| `dst_port` | pandas nullable `Int64`; TCP/UDP destination port, otherwise `pd.NA` |
| `protocol` | One exclusive display category: `DNS`, `TCP`, `UDP`, `ICMP`, or `OTHER` |
| `transport` | Independent underlying transport: `TCP`, `UDP`, `ICMP`, or `OTHER` |
| `length` | Packet length, `int64` |
| `tcp_flags` | String such as `S`, `SA`, `A`, `PA`; `None` for non-TCP |
| `ip_version` | pandas nullable `Int64`; `4` or `6`, otherwise `pd.NA` |
| `dns_query` | Decoded DNS query name; `None` when not applicable |

Protocol classification precedence is frozen:

```python
if DNS layer exists:
    protocol = "DNS"
elif TCP exists:
    protocol = "TCP"
elif UDP exists:
    protocol = "UDP"
elif ICMP / ICMPv6 exists:
    protocol = "ICMP"
else:
    protocol = "OTHER"
```

Transport is tracked independently. DNS over UDP has `protocol = "DNS"`
and `transport = "UDP"`. Classification precedence is distinct from display
ordering in `PROTOCOL_ORDER`.

`DetectionConfig` is a frozen dataclass with these exact typed defaults:

```python
@dataclass(frozen=True)
class DetectionConfig:
    port_scan_unique_ports: int = 100
    port_scan_window_seconds: float = 60.0
    high_rate_packets: int = 300
    high_rate_window_seconds: float = 10.0
```

## Frozen public APIs

Preserve these signatures and return types. The parser, statistics, and anomaly
APIs describe future implementation work by their owners; they do not imply
those modules exist in the scaffold.

```python
# analyzer/parser.py
parse_capture_bytes(
    data: bytes,
    filename: str,
    *,
    max_packets: int = MAX_PACKETS,
) -> tuple[pandas.DataFrame, dict[str, object]]

# analyzer/statistics.py
calculate_statistics(
    packets: pandas.DataFrame,
) -> dict[str, object]

# analyzer/anomaly_detector.py
detect_anomalies(
    packets: pandas.DataFrame,
    config: DetectionConfig | None = None,
) -> list[dict[str, object]]

# analyzer/service.py
analyze_capture(
    data: bytes,
    filename: str,
    config: DetectionConfig | None = None,
) -> dict[str, object]
```

## Frozen analysis result

The eventual AnalysisResult from `analyze_capture` must contain exactly these
top-level fields. Do not silently add, remove, or rename them:

```python
{
    "schema_version": "1.0",
    "metadata": ...,
    "summary": ...,
    "protocol_distribution": ...,
    "top_sources": ...,
    "top_destinations": ...,
    "packet_sizes": ...,
    "timeline": ...,
    "alerts": ...,
    "packets": ...,
}
```

`metadata` will contain `filename`, `file_size_bytes`, `format`,
`parsed_packets`, `truncated`, `start_time`, `end_time`, `duration_seconds`,
and `warnings`.

`summary` will contain `total_packets`, `total_bytes`, `average_packet_size`,
`min_packet_size`, `max_packet_size`, `unique_sources`, `unique_destinations`,
and `alert_count`.

`packets` must remain a pandas DataFrame. Do not convert it to JSON.
Nested structures not specified here must be agreed during integration;
do not infer additional frozen fields.

## Current scaffold scope and validation

Task 1 creates only `requirements.txt`, `.gitignore`, `AGENTS.md`,
`analyzer/__init__.py`, `analyzer/contracts.py`, `analyzer/service.py`,
and `tests/test_service.py`. The service is a typed stub that raises
`NotImplementedError` until integration. It must not fabricate results or
import/duplicate unimplemented parser, statistics, or anomaly modules.

Do not implement the parser, statistics engine, anomaly detector, frontend,
demo PCAP generator, or documentation during Task 1. Do not create teammate
placeholder files. Leave `README.md` untouched.

Run tests from the repository root:

```sh
python -m pytest -q
```

Smoke tests must verify only existing contracts and stub behavior. Report
missing pytest/dependencies instead of making unrelated environment changes.
