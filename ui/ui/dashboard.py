"""Dashboard layout, functional views, and a read-only packet inspector."""

import streamlit as st

from analyzer.contracts import MAX_FILE_BYTES, MAX_PACKETS, PROTOCOL_ORDER, DetectionConfig
from ui.charts import protocol_distribution, traffic_timeline
from ui.components import (
    byte_size, capture_information, kpi_cards, packet_sizes, panel_title,
    security_alerts, top_talkers,
)


def packet_inspector(result: dict[str, object], *, compact: bool = False) -> None:
    packets = result["packets"]
    panel_title("Packet Preview" if compact else "Packet Inspector", "table")
    prefix = "preview" if compact else "packet"
    search, protocol = st.columns([2, 1], gap="small")
    with search:
        query = st.text_input("Search IP / DNS text", key=f"{prefix}_search", placeholder="IP address or DNS query…")
    with protocol:
        selected = st.selectbox("Protocol filter", ["All protocols", *PROTOCOL_ORDER], key=f"{prefix}_protocol")
    filtered = packets
    if selected != "All protocols":
        filtered = filtered.loc[filtered["protocol"] == selected]
    if query:
        matches = filtered["src_ip"].astype("string").str.contains(query, regex=False, na=False)
        for column in ("dst_ip", "dns_query"):
            matches |= filtered[column].astype("string").str.contains(query, regex=False, na=False)
        filtered = filtered.loc[matches]
    columns = ["timestamp", "src_ip", "dst_ip", "src_port", "dst_port", "protocol", "transport", "length", "tcp_flags", "dns_query"]
    preview = filtered.loc[:, columns].head(500).copy()
    # Presentation strings belong only in this bounded copy, never the service frame.
    for column in ("src_ip", "dst_ip", "src_port", "dst_port", "tcp_flags", "dns_query"):
        preview[column] = preview[column].astype("string").fillna("—")
    preview["timestamp"] = preview["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S.%f").str.slice(stop=-3).fillna("—")
    st.caption(f"Showing {len(preview):,} of {len(packets):,} packets" + (f" · {len(filtered):,} match filters" if query or selected != "All protocols" else ""))
    st.dataframe(
        preview, hide_index=True, width="stretch", height=235 if compact else 520,
        column_config={
            "timestamp": "Timestamp (UTC)",
            "src_ip": "Source IP", "dst_ip": "Destination IP", "src_port": "Src Port",
            "dst_port": "Dst Port", "protocol": "Protocol", "transport": "Transport",
            "length": st.column_config.NumberColumn("Length (B)", format="%d"),
            "tcp_flags": "TCP Flags", "dns_query": "DNS Query",
        },
    )


def chart_row(result: dict[str, object], *, metadata: bool = True) -> None:
    with st.container(key="overview_charts"):
        columns = st.columns([1.05, 1.25, 1.05] if metadata else [1, 1.5], gap="small")
        with columns[0], st.container(key="panel_protocol"):
            protocol_distribution(result["protocol_distribution"])
        with columns[1], st.container(key="panel_timeline"):
            traffic_timeline(result["timeline"])
        if metadata:
            with columns[2], st.container(key="panel_capture"):
                capture_information(result["metadata"])


def ranking_row(result: dict[str, object], *, compact: bool = True) -> None:
    with st.container(key="overview_rankings"):
        sources, destinations, sizes = st.columns([1.1, 1.1, 1], gap="small")
        with sources, st.container(key="panel_sources"):
            top_talkers(result["top_sources"], "Top Source IPs", limit=5 if compact else None)
        with destinations, st.container(key="panel_destinations"):
            top_talkers(result["top_destinations"], "Top Destination IPs", violet=True, limit=5 if compact else None)
        with sizes, st.container(key="panel_sizes"):
            packet_sizes(result["packet_sizes"])


def render_settings() -> None:
    config = DetectionConfig()
    with st.container(key="panel_settings"):
        panel_title("Analysis Settings", "settings", "Current defaults · read-only")
        left, right = st.columns(2)
        with left:
            st.markdown("**Possible port scan**")
            st.write(f"{config.port_scan_unique_ports} unique destination ports within {config.port_scan_window_seconds:g} seconds.")
            st.caption("Initial TCP SYN packets without ACK, grouped by source and destination.")
        with right:
            st.markdown("**High packet rate**")
            st.write(f"{config.high_rate_packets} packets from one source within {config.high_rate_window_seconds:g} seconds.")
            st.caption("Counts all packets with a source IP and usable timestamp.")
        st.divider()
        st.caption(f"Capture limit: {byte_size(MAX_FILE_BYTES)} · Parser limit: {MAX_PACKETS:,} packets · Timezone: UTC")
        st.info("This application analyzes saved captures. It does not capture or transmit live network traffic.", icon=":material/info:")


def render_dashboard(result: dict[str, object], view: str) -> None:
    if view == "Overview":
        kpi_cards(result)
        chart_row(result)
        ranking_row(result)
        with st.container(key="panel_alerts"):
            security_alerts(result["alerts"])
        with st.container(key="panel_packets"):
            packet_inspector(result, compact=True)
    elif view == "Security Alerts":
        with st.container(key="panel_alerts"):
            security_alerts(result["alerts"], expanded=True)
        config = DetectionConfig()
        st.caption(f"Heuristic defaults: {config.port_scan_unique_ports} unique TCP SYN ports / {config.port_scan_window_seconds:g}s; {config.high_rate_packets} packets per source / {config.high_rate_window_seconds:g}s. Patterns are not a confirmation of malicious intent.")
    elif view == "Packet Analysis":
        with st.container(key="panel_packets"):
            packet_inspector(result)
    elif view == "Statistics":
        kpi_cards(result)
        chart_row(result, metadata=False)
        ranking_row(result, compact=False)
        with st.container(key="panel_capture"):
            capture_information(result["metadata"])
