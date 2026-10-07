"""Offline Streamlit frontend for the frozen Python analysis service."""

from hashlib import sha256
from pathlib import Path

import streamlit as st

from analyzer.service import analyze_capture
from ui.components import icon, install_styles, window_header
from ui.dashboard import render_dashboard, render_settings


ROOT = Path(__file__).resolve().parent
DEMO_NAMES = (
    "normal_traffic.pcap", "normal_traffic.pcapng", "port_scan.pcap",
    "high_rate.pcap", "suspicious_traffic.pcap",
)
VIEWS = ("Overview", "Security Alerts", "Packet Analysis", "Statistics", "Settings")
NAV_MARKS = ("dashboard", "warning", "table_chart", "bar_chart", "settings")


def load_capture(data: bytes, filename: str, *, source: str) -> None:
    """Analyze only a new input; retain the last valid result if input fails."""
    if Path(filename).suffix.lower() not in {".pcap", ".pcapng"}:
        st.session_state["analysis_error"] = "Choose a .pcap or .pcapng capture file."
        return
    digest = sha256(data).hexdigest() + ":" + filename
    if digest == st.session_state.get("analysis_digest"):
        st.session_state["analysis_error"] = None
        return
    try:
        with st.spinner("Analyzing capture…"):
            result = analyze_capture(data, filename)
    except ValueError as error:
        st.session_state["analysis_error"] = str(error)
        return
    st.session_state["analysis_result"] = result
    st.session_state["analysis_digest"] = digest
    st.session_state["analysis_source"] = source
    st.session_state["analysis_error"] = None


def load_demo(name: str) -> None:
    path = ROOT / "samples" / name
    try:
        data = path.read_bytes()
    except OSError:
        st.session_state["analysis_error"] = f"Demo capture {name} is unavailable."
        return
    load_capture(data, name, source="Built-in demo")


def main() -> None:
    st.set_page_config(
        page_title="Network Traffic Analyzer", page_icon="◈", layout="wide",
        initial_sidebar_state="expanded",
    )
    install_styles()
    if "initialized" not in st.session_state:
        st.session_state["initialized"] = True
        load_demo("normal_traffic.pcap")

    with st.sidebar:
        st.markdown(f'<div class="app-brand"><span class="app-mark">{icon("activity")}</span><span>Network Traffic Analyzer</span></div>', unsafe_allow_html=True)
        view = st.radio(
            "Navigation", VIEWS, key="navigation", label_visibility="collapsed", width="stretch",
            format_func=lambda name: f":material/{NAV_MARKS[VIEWS.index(name)]}:  {name}",
        )
        with st.container(key="sidebar_demos"):
            st.markdown('<div class="eyebrow">BUILT-IN DEMO CAPTURES</div>', unsafe_allow_html=True)
            for index, name in enumerate(DEMO_NAMES):
                st.button(
                    name, key=f"demo_{index}", icon=":material/description:",
                    width="stretch", on_click=load_demo, args=(name,),
                )
            st.markdown('<div class="sidebar-note"><span class="status-dot"></span> Offline capture analysis<br><span>PCAP & PCAPNG · No live traffic</span></div>', unsafe_allow_html=True)

    with st.container(key="main_header"):
        title, controls = st.columns([2.1, 1.4], vertical_alignment="center")
        with title:
            window_header()
        with controls:
            upload, demo = st.columns(2, gap="small")
            with upload:
                with st.popover("Upload Capture", icon=":material/upload:", width="stretch"):
                    st.markdown("**Open a capture**")
                    st.caption("Offline analysis · maximum 25 MiB")
                    capture = st.file_uploader(
                        "PCAP or PCAPNG file", type=["pcap", "pcapng"],
                        max_upload_size=25, key="capture_upload",
                    )
                    if st.button("Analyze Capture", type="primary", width="stretch", disabled=capture is None):
                        load_capture(capture.getvalue(), capture.name, source="Uploaded capture")
            with demo:
                with st.popover("Demo Capture", type="primary", icon=":material/folder_open:", width="stretch"):
                    selected = st.selectbox("Built-in demo", DEMO_NAMES, key="header_demo")
                    st.button("Open Demo", type="primary", width="stretch", on_click=load_demo, args=(selected,))

    if st.session_state.get("analysis_error"):
        st.error(st.session_state["analysis_error"], icon=":material/error:")
        if "analysis_result" in st.session_state:
            st.caption("The previous valid capture remains open below.")
    result = st.session_state.get("analysis_result")
    if view == "Settings":
        render_settings()
    elif result is not None:
        render_dashboard(result, view)
    else:
        st.info("Upload a capture or open a built-in demo to get started.", icon=":material/folder_open:")


if __name__ == "__main__":
    main()
