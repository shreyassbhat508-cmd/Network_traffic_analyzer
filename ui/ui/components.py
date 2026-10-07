"""Reusable, escaped HTML presentation and native Streamlit panels."""

from collections import Counter
from datetime import datetime, timedelta, timezone
from html import escape

import streamlit as st


FONT = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", sans-serif'
COLORS = {"TCP": "#258cff", "UDP": "#9059f5", "ICMP": "#dd5b9b", "DNS": "#ffa85b", "OTHER": "#8190a3"}


def h(value: object) -> str:
    return escape(str(value))


def byte_size(value: float) -> str:
    size = float(value)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if abs(size) < 1024 or unit == "GiB":
            return f"{size:,.0f} {unit}" if unit == "B" else f"{size:,.1f} {unit}"
        size /= 1024
    return "0 B"


def timestamp_text(value: object) -> str:
    if value is None:
        return "—"
    try:
        instant = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return str(value)
    if instant.tzinfo is not None:
        instant = instant.astimezone(timezone.utc)
    instant += timedelta(microseconds=round(instant.microsecond / 1000) * 1000 - instant.microsecond)
    fraction = f".{instant.microsecond // 1000:03d}".rstrip("0") if instant.microsecond else ""
    return instant.strftime("%d %b %Y, %H:%M:%S") + fraction + " UTC"


def timestamp_range(start: object, end: object) -> str:
    start_text, end_text = timestamp_text(start), timestamp_text(end)
    start_day, separator, start_clock = start_text.partition(", ")
    end_day, _, end_clock = end_text.partition(", ")
    if separator and start_day == end_day:
        return f'{start_day} · {start_clock.removesuffix(" UTC")} – {end_clock}'
    return f"{start_text} → {end_text}"


def icon(name: str) -> str:
    """Small, consistent utility symbols; paths are controlled UI markup."""
    paths = {
        "activity": '<path d="M2 12h4l3-8 5 16 3-8h5"/>',
        "packets": '<path d="m3 7 9-4 9 4-9 4-9-4Zm0 5 9 4 9-4M3 17l9 4 9-4"/>',
        "bytes": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v7c0 4 16 4 16 0V5M4 12v7c0 4 16 4 16 0v-7"/>',
        "source": '<circle cx="9" cy="7" r="3"/><path d="M3 20v-3a6 6 0 0 1 12 0v3M17 9h5m-2-2 2 2-2 2"/>',
        "destination": '<circle cx="8" cy="7" r="3"/><path d="M2 20v-3a6 6 0 0 1 12 0v3M17 4a3 3 0 0 1 0 6m0 4a5 5 0 0 1 5 5v1"/>',
        "alerts": '<path d="m12 3 10 18H2L12 3Zm0 6v5m0 3v.2"/>',
        "table": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11M15 9v11M3 14h18"/>',
        "chart": '<path d="M4 20V10m5 10V4m6 16v-7m5 7V7"/>',
        "file": '<path d="M14 3H5v18h14V8l-5-5Zm0 0v5h5M8 12h8m-8 4h8"/>',
        "settings": '<circle cx="12" cy="12" r="7"/><circle cx="12" cy="12" r="2"/><path d="M12 2v3m0 14v3M2 12h3m14 0h3M5 5l2 2m10 10 2 2M5 19l2-2M17 7l2-2"/>',
    }
    return '<svg class="utility-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths.get(name, paths["chart"]) + '</svg>'


def install_styles() -> None:
    st.markdown(f"""<style>
    :root {{ --panel:#111b2a; --muted:#91a0b5; --border:rgba(176,200,238,.12); }}
    html, body, [data-testid="stApp"], [data-testid="stSidebar"] {{ font-family:{FONT}; }}
    [data-testid="stMarkdownContainer"], [data-testid="stApp"] p, [data-testid="stApp"] button {{ font-family:{FONT} !important; }}
    [data-testid="stAppViewContainer"] {{ background:#080f19; }}
    [data-testid="stHeader"] {{ background:transparent; height:0 !important; min-height:0 !important; }}
    /* Keep Streamlit's real sidebar control reachable when the sidebar is collapsed. */
    [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) [data-testid="stHeader"] {{ height:44px !important; min-height:44px !important; pointer-events:none; }}
    [data-testid="stHeader"] button {{ pointer-events:auto; }}
    [data-testid="stAppViewContainer"]:has([data-testid="stSidebar"][aria-expanded="false"]) .st-key-main_header [data-testid="stMarkdownContainer"]:has(> .main-subtitle) {{ padding-left:42px; }}
    [data-testid="stMainBlockContainer"] {{ max-width:1800px; padding:1.5rem 1.15rem 1.3rem; }}
    [data-testid="stMain"] [data-testid="stVerticalBlock"] {{ gap:.55rem; }}
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {{ gap:16px; }}
    .st-key-main_header {{ margin-bottom:4px; }}
    /* Streamlit's paragraph compensation must not subtract height from our HTML panels. */
    [data-testid="stMarkdownContainer"]:has(> :is(.app-brand,.eyebrow,.sidebar-note,.main-title,.main-subtitle,.kpi,.panel-title,.panel-subtitle,.capture-info,.protocol-legend,.talker-row,.size-grid,.alert-row,.empty-alert)) {{ margin-bottom:0; }}
    [data-testid="stElementContainer"]:has([data-testid="stMarkdownContainer"] > style) {{ display:none; }}
    .utility-icon {{ width:18px; height:18px; display:block; flex-shrink:0; }}
    [data-testid="stSidebar"] {{ width:255px !important; min-width:255px !important; background:linear-gradient(170deg,#121d2d,#0c1422 75%); border-right:1px solid var(--border); }}
    [data-testid="stSidebarContent"] {{ padding:0; }}
    [data-testid="stSidebarHeader"] {{ height:0; min-height:0; padding:0; }}
    [data-testid="stLogoSpacer"] {{ display:none; }}
    [data-testid="stSidebarCollapseButton"] {{ position:absolute; top:8px; right:7px; z-index:2; }}
    [data-testid="stSidebarUserContent"] {{ padding:1.1rem .7rem; }}
    .app-brand {{ display:flex; align-items:center; gap:8px; font-size:12px; font-weight:600; white-space:nowrap; padding:4px 3px 18px; }}
    .app-mark {{ display:grid; place-items:center; width:25px; height:25px; flex-shrink:0; border-radius:7px; background:#1477eb; color:white; }}
    [data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {{ gap:3px; }}
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] {{ width:100%; }}
    [data-testid="stSidebar"] [data-testid="stRadioGroup"] > div {{ width:100%; }}
    [data-testid="stSidebar"] [data-testid="stRadioOption"] {{ padding:8px 12px; border-radius:10px; margin:0; min-height:38px; width:100%; color:#b8c3d3; }}
    [data-testid="stSidebar"] [data-testid="stRadioOption"] > div > div:first-child {{ display:none; }}
    [data-testid="stSidebar"] [data-testid="stRadioOption"][data-selected="true"] {{ background:rgba(44,132,255,.21); color:#f1f5fc; box-shadow:inset 0 0 0 1px rgba(73,141,237,.13); }}
    [data-testid="stSidebar"] [data-testid="stRadioOption"] p {{ font-size:13px; }}
    .st-key-sidebar_demos {{ margin-top:clamp(36px,15vh,170px); }}
    .eyebrow {{ font-size:10px; font-weight:650; letter-spacing:1.3px; color:#75879f; padding:0 7px 8px; }}
    [data-testid="stSidebar"] .st-key-sidebar_demos button {{ justify-content:flex-start; background:transparent; border:1px solid transparent !important; color:#aab8ca; min-height:34px; padding:4px 8px; font-size:11px; border-radius:9px; }}
    [data-testid="stSidebar"] .st-key-sidebar_demos button p {{ font-size:12px !important; }}
    [data-testid="stSidebar"] .st-key-sidebar_demos button:hover {{ background:#18243a; border-color:var(--border); }}
    .sidebar-note {{ border-top:1px solid var(--border); margin-top:18px; padding:16px 6px 0; font-size:11px; line-height:1.8; color:#bbc6d5; }}
    .sidebar-note > span:last-child {{ color:#73839a; font-size:10px; }}
    .status-dot {{ display:inline-block; width:5px; height:5px; border-radius:50%; background:#67b3ff; margin-right:5px; vertical-align:middle; }}
    h1.main-title {{ margin:0 !important; padding:0 !important; font-size:29px !important; line-height:1.16 !important; font-family:{FONT} !important; font-weight:650 !important; letter-spacing:-.75px; color:#f6f8fc; }}
    p.main-subtitle {{ font-size:12px !important; color:#9aabc2; margin:8px 0 0 !important; line-height:1.45 !important; }}
    .st-key-main_header [data-testid="stPopover"] button {{ height:38px; min-height:38px; padding:0 10px; border-radius:11px !important; }}
    button, [data-testid="stPopover"] button {{ border-radius:12px !important; border-color:rgba(166,190,224,.16) !important; }}
    [data-testid="stBaseButton-primary"] {{ background:#258cff; box-shadow:0 3px 14px rgba(0,91,255,.16); }}
    [data-testid="stBaseButton-secondary"] {{ background:#17253a; }}
    button p {{ font-size:12px; }}
    [data-testid="stCaptionContainer"] p {{ color:#8091a8; font-size:11px; }}
    .kpi {{ background:linear-gradient(145deg,rgba(29,45,65,.7),rgba(14,23,37,.92)); border:1px solid var(--border); border-radius:18px; padding:13px; min-height:114px; box-sizing:border-box; box-shadow:inset 0 1px rgba(255,255,255,.035),0 6px 20px rgba(0,0,0,.12); }}
    .kpi-top {{ display:flex; gap:8px; align-items:center; }}
    .kpi-icon {{ display:grid; place-items:center; width:25px; height:25px; flex-shrink:0; background:rgba(50,140,255,.18); color:#80bdff; border-radius:7px; }}
    .kpi-icon .utility-icon {{ width:16px; height:16px; }}
    .kpi-icon.violet {{ background:rgba(145,89,245,.18); color:#bb96ff; }}
    .kpi-icon.cyan {{ background:rgba(30,183,190,.16); color:#69d3d8; }}
    .kpi-icon.red {{ background:rgba(239,80,92,.18); color:#ff8d97; }}
    .kpi-label {{ font-size:11px; color:#b7c4d6; line-height:1.3; min-height:28px; display:flex; align-items:center; }}
    .kpi-value {{ font-size:25px; font-weight:650; letter-spacing:-.5px; line-height:1.15; margin-top:8px; font-variant-numeric:tabular-nums; }}
    .kpi-foot {{ font-size:10px; color:#798da8; line-height:14px; margin-top:6px; min-height:14px; }}
    [data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {{ border-radius:19px; }}
    div[class*="st-key-panel_"] {{ background:linear-gradient(150deg,rgba(23,36,53,.9),rgba(12,21,34,.97)); border:1px solid var(--border); border-radius:19px; padding:15px 14px; min-width:0; box-shadow:inset 0 1px rgba(255,255,255,.035),0 7px 24px rgba(0,0,0,.12); }}
    .panel-title {{ display:flex; gap:8px; align-items:center; margin:0; font-size:14px; font-weight:600; color:#f0f4fa; }}
    .panel-title > span {{ color:#85bfff; font-size:16px; }}
    .panel-subtitle {{ color:#8395ac; font-size:11px; margin:0; }}
    .capture-info {{ margin:4px 0 0; }}
    .capture-info > div {{ display:grid; grid-template-columns:37% minmax(0,1fr); gap:8px; padding:4px 0; font-size:11px; line-height:1.45; }}
    .capture-info dt {{ color:#91a0b5; }} .capture-info dd {{ margin:0; color:#d2dbe7; overflow-wrap:anywhere; }}
    .protocol-legend {{ padding:13px 0 0 3px; }}
    .protocol-legend > div {{ display:grid; grid-template-columns:8px 1fr auto; align-items:center; gap:8px; font-size:11px; padding:7px 0; color:#cbd6e5; }}
    .legend-dot {{ width:8px; height:8px; border-radius:50%; }}
    .legend-number {{ color:#90a1b8; font-variant-numeric:tabular-nums; }}
    .talker-row {{ display:grid; grid-template-columns:12px minmax(90px,1fr) minmax(35px,1fr) 53px; align-items:center; gap:8px; padding:5px 0; font-size:12px; }}
    .talker-rank {{ color:#748aa5; font-size:10px; }} .talker-ip {{ color:#dbe3ef; overflow-wrap:anywhere; font-family:ui-monospace,SFMono-Regular,Consolas,monospace; font-size:11px; }}
    .talker-track {{ height:6px; background:rgba(115,147,194,.08); border-radius:6px; overflow:hidden; }}
    .talker-bar {{ height:100%; background:#258cff; border-radius:6px; }} .talker-bar.violet {{ background:#9059f5; }}
    .talker-count {{ text-align:right; color:#c0cddd; font-variant-numeric:tabular-nums; }}
    .talker-count small {{ display:block; font-size:10px; color:#788da8; margin-top:2px; }}
    .size-grid {{ display:grid; grid-template-columns:repeat(6,minmax(0,1fr)); gap:7px; }}
    .size-cell {{ grid-column:span 2; background:rgba(113,148,199,.06); border:1px solid rgba(173,202,249,.05); border-radius:12px; padding:10px; min-height:65px; box-sizing:border-box; }}
    .size-label {{ color:#8c9eb6; font-size:10px; line-height:14px; }} .size-value {{ font-size:20px; font-weight:600; margin-top:6px; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }}
    .size-cell:nth-last-child(-n+2) {{ grid-column:span 3; }}
    .alert-row {{ display:grid; grid-template-columns:72px 1fr minmax(170px,.75fr); gap:7px 12px; align-items:center; border-left:3px solid #ec5b69; border-radius:12px; background:rgba(147,52,69,.10); padding:11px 13px; margin-bottom:6px; border-top:1px solid rgba(248,93,113,.12); border-bottom:1px solid rgba(248,93,113,.12); }}
    .alert-row.medium {{ border-left-color:#e9a64a; background:rgba(139,94,33,.10); border-top-color:rgba(233,166,74,.12); border-bottom-color:rgba(233,166,74,.12); }}
    .severity {{ font-size:10px; font-weight:650; color:#ff9da5; border-radius:6px; background:rgba(246,85,102,.18); padding:5px 8px; width:fit-content; }}
    .medium .severity {{ color:#f8c175; background:rgba(233,166,74,.18); }}
    .alert-type {{ font-size:12px; font-weight:600; letter-spacing:.2px; }}
    .alert-detail {{ color:#9aabc0; font-size:11px; margin-top:5px; line-height:1.45; overflow-wrap:anywhere; }}
    .alert-evidence {{ font-size:12px; color:#e7edf6; text-align:right; }}
    .alert-time {{ font-size:10px; color:#93a3b9; margin-top:5px; line-height:1.4; }}
    .alert-context {{ grid-column:2 / -1; font-size:11px; color:#adbacd; line-height:1.5; }}
    .evidence-chips {{ display:flex; flex-wrap:wrap; gap:4px; margin-top:6px; }}
    .evidence-chip {{ border:1px solid rgba(172,190,216,.10); border-radius:5px; background:rgba(139,153,179,.04); padding:2px 6px; font-size:10px; color:#8f9fb5; overflow-wrap:anywhere; max-width:100%; }}
    .empty-alert {{ padding:15px; border:1px solid var(--border); border-radius:12px; background:rgba(40,107,158,.06); color:#c6d5e8; font-size:12px; }}
    [data-testid="stDataFrame"] {{ border-radius:12px; border:1px solid var(--border); overflow:hidden; }}
    [data-testid="stTextInput"] input {{ font-size:12px; }}
    [data-testid="stAlert"] {{ border-radius:12px; font-size:12px; }}
    [data-testid="stBottomBlockContainer"] {{ display:none; }}
    @media(max-width:1200px) {{
      h1.main-title {{ font-size:25px !important; }} .kpi {{ padding:12px 10px; }} .kpi-value {{ font-size:21px; }}
      .st-key-overview_charts > div > [data-testid="stHorizontalBlock"], .st-key-overview_rankings > div > [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap; }}
      .st-key-overview_charts > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"], .st-key-overview_rankings > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ min-width:280px; flex:1; }}
    }}
    @media(max-width:800px) {{
      [data-testid="stMainBlockContainer"] {{ padding:1.1rem .8rem 1rem; }}
      h1.main-title {{ font-size:24px !important; }} .alert-row {{ grid-template-columns:70px 1fr; }} .alert-evidence {{ grid-column:2; text-align:left; }}
    }}
    @media(max-width:1100px) {{
      .st-key-main_header > div > [data-testid="stHorizontalBlock"], .st-key-kpi_row > div > [data-testid="stHorizontalBlock"] {{ flex-wrap:wrap; }}
      .st-key-main_header > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ min-width:300px; flex:1; }}
      .st-key-kpi_row > div > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ min-width:150px; flex:1 1 calc(33.333% - 12px); }}
    }}
    </style>""", unsafe_allow_html=True)


def window_header() -> None:
    st.markdown('<h1 class="main-title">Network Traffic Analyzer</h1><p class="main-subtitle">Offline PCAP analysis, traffic statistics and deterministic anomaly detection</p>', unsafe_allow_html=True)


def panel_title(title: str, mark: str = "chart", subtitle: str | None = None) -> None:
    st.markdown(f'<div class="panel-title"><span>{icon(mark)}</span>{h(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="panel-subtitle">{h(subtitle)}</div>', unsafe_allow_html=True)


def kpi_cards(result: dict[str, object]) -> None:
    summary = result["summary"]
    severities = Counter(alert["severity"] for alert in result["alerts"])
    cards = [
        ("Total Packets", f'{summary["total_packets"]:,}', "packets", "violet", "Parsed capture packets"),
        ("Total Bytes", byte_size(summary["total_bytes"]), "bytes", "cyan", f'{summary["total_bytes"]:,} bytes'),
        ("Avg Packet Size", byte_size(summary["average_packet_size"]), "activity", "cyan", "Mean captured length"),
        ("Unique Sources", f'{summary["unique_sources"]:,}', "source", "", "Source IP addresses"),
        ("Unique Destinations", f'{summary["unique_destinations"]:,}', "destination", "", "Destination IP addresses"),
        ("Alerts", str(summary["alert_count"]), "alerts", "red", f'{severities["HIGH"]} High · {severities["MEDIUM"]} Medium'),
    ]
    with st.container(key="kpi_row"):
        columns = st.columns(6, gap="small")
    for column, (label, value, mark, color, foot) in zip(columns, cards):
        with column:
            st.markdown(f'<div class="kpi"><div class="kpi-top"><span class="kpi-icon {color}">{icon(mark)}</span><span class="kpi-label">{h(label)}</span></div><div class="kpi-value">{h(value)}</div><div class="kpi-foot">{h(foot)}</div></div>', unsafe_allow_html=True)


def capture_information(metadata: dict[str, object]) -> None:
    panel_title("Capture Information", "file")
    rows = [
        ("Filename", metadata["filename"]), ("Format", metadata["format"]),
        ("Parsed Packets", f'{metadata["parsed_packets"]:,}'),
        ("Capture Start", timestamp_text(metadata["start_time"])),
        ("Capture End", timestamp_text(metadata["end_time"])),
        ("Duration", f'{metadata["duration_seconds"]:,.3f}'.rstrip("0").rstrip(".") + " seconds"),
        ("Truncated", "Yes" if metadata["truncated"] else "No"),
    ]
    st.markdown('<dl class="capture-info">' + ''.join(f'<div><dt>{h(label)}</dt><dd>{h(value)}</dd></div>' for label, value in rows) + '</dl>', unsafe_allow_html=True)
    for warning in metadata["warnings"]:
        st.warning(str(warning), icon=":material/warning:")


def top_talkers(rows: list[dict[str, object]], title: str, *, violet: bool = False, limit: int | None = 5) -> None:
    shown = rows if limit is None else rows[:limit]
    panel_title(title, "destination" if violet else "source", f"Top {len(shown)} · packets & captured bytes")
    if not rows:
        st.caption("No IP addresses in this capture.")
        return
    maximum = max(row["packets"] for row in rows) or 1
    markup = []
    for rank, row in enumerate(shown, 1):
        width = 100 * row["packets"] / maximum
        markup.append(f'<div class="talker-row"><span class="talker-rank">{rank}</span><span class="talker-ip">{h(row["ip"])}</span><div class="talker-track"><div class="talker-bar {"violet" if violet else ""}" style="width:{width:.2f}%"></div></div><span class="talker-count">{row["packets"]:,}<small>{h(byte_size(row["bytes"]))}</small></span></div>')
    st.markdown(''.join(markup), unsafe_allow_html=True)


def packet_sizes(sizes: dict[str, object]) -> None:
    panel_title("Packet Size Statistics", "chart")
    labels = (("Minimum", "min"), ("Maximum", "max"), ("Mean", "mean"), ("Median", "median"), ("95th Percentile", "p95"))
    st.markdown('<div class="size-grid">' + ''.join(f'<div class="size-cell"><div class="size-label">{label}</div><div class="size-value">{h(byte_size(sizes[key]))}</div></div>' for label, key in labels) + '</div>', unsafe_allow_html=True)


def security_alerts(alerts: list[dict[str, object]], *, expanded: bool = False) -> None:
    panel_title(f"Security Alerts · {len(alerts)}", "alerts")
    if not alerts:
        st.markdown('<div class="empty-alert">No anomaly patterns detected by the configured heuristics.</div>', unsafe_allow_html=True)
        st.caption("This does not guarantee that the capture is free of malicious activity.")
        return
    for alert in alerts if expanded else alerts[:4]:
        evidence = alert["evidence"]
        if alert["type"] == "POSSIBLE_PORT_SCAN":
            prominent = f'{evidence["unique_destination_ports"]:,} unique destination ports'
        else:
            prominent = f'{evidence["packets"]:,} packets · {evidence["packets_per_second"]:,.1f} pkt/s'
        endpoints = f'Source: {alert["source_ip"]}'
        if alert["destination_ip"] is not None:
            endpoints += f' → {alert["destination_ip"]}'
        primary_keys = {"unique_destination_ports"} if alert["type"] == "POSSIBLE_PORT_SCAN" else {"packets", "packets_per_second"}
        chips = ''.join(f'<span class="evidence-chip">{h(key.replace("_", " "))}: {h(value)}</span>' for key, value in evidence.items() if key not in primary_keys)
        title = alert["type"].replace("_", " ").title()
        time_range = timestamp_range(alert["start_time"], alert["end_time"])
        st.markdown(f'<div class="alert-row {"medium" if alert["severity"] == "MEDIUM" else ""}"><div class="severity">{h(alert["severity"])}</div><div><div class="alert-type">{h(title)}</div><div class="alert-detail">{h(endpoints)}</div></div><div class="alert-evidence">{h(prominent)}<div class="alert-time">{h(time_range)}</div></div><div class="alert-context">{h(alert["message"])}<div class="evidence-chips">{chips}</div></div></div>', unsafe_allow_html=True)
    if not expanded and len(alerts) > 4:
        st.caption(f"{len(alerts) - 4} additional patterns. Open Security Alerts to inspect all evidence.")
