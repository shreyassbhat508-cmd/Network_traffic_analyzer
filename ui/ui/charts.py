"""Plotly figures driven exclusively by real service result sections."""

from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from ui.components import COLORS, FONT, h, panel_title


def protocol_distribution(rows: list[dict[str, object]]) -> None:
    panel_title("Protocol Distribution", "packets")
    if not sum(row["packets"] for row in rows):
        st.info("No packets to classify.")
        return
    chart, legend = st.columns([1.05, 1], gap="small")
    with chart:
        total = sum(row["packets"] for row in rows)
        figure = go.Figure(go.Pie(
            labels=[row["protocol"] for row in rows], values=[row["packets"] for row in rows],
            hole=.72, sort=False, textinfo="none", direction="clockwise",
            marker={"colors": [COLORS[row["protocol"]] for row in rows], "line": {"width": 1, "color": "#142033"}},
            hovertemplate="%{label}<br>%{value:,} packets · %{percent}<extra></extra>",
        ))
        figure.update_layout(
            height=180, margin={"l": 2, "r": 5, "t": 9, "b": 9}, showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font={"family": FONT, "color": "#b9c7d9", "size": 11},
            annotations=[{"text": f"<b>{total:,}</b><br><span style='font-size:10px'>Packets</span>", "x": .5, "y": .5, "showarrow": False, "font": {"size": 15, "color": "#edf3fc"}}],
            hoverlabel={"bgcolor": "#1a293e", "font_size": 12},
        )
        st.plotly_chart(figure, theme=None, config={"displayModeBar": False}, width="stretch")
    with legend:
        st.markdown('<div class="protocol-legend">' + ''.join(f'<div><i class="legend-dot" style="background:{COLORS[row["protocol"]]}"></i><span>{h(row["protocol"])} <span class="legend-number">{row["percent"]:.1f}%</span></span><span class="legend-number">{row["packets"]:,}</span></div>' for row in rows) + '</div>', unsafe_allow_html=True)


def traffic_timeline(rows: list[dict[str, object]]) -> None:
    panel_title("Traffic Timeline", "activity")
    if not rows:
        st.info("No usable timestamps to plot.")
        return
    instants = [datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00")) for row in rows]
    duration = (max(instants) - min(instants)).total_seconds()
    cross_date = min(instants).date() != max(instants).date()
    tick_format = "%d %b<br>%H:%M" if cross_date else "%H:%M:%S" if duration <= 120 else "%H:%M"
    # Label a few actual buckets, without resampling or inventing traffic values.
    tick_indices = sorted({round(index * (len(rows) - 1) / 3) for index in range(4)})
    tick_labels = [instants[index].strftime(tick_format) for index in tick_indices]
    if len(set(tick_labels)) < len(tick_labels):
        tick_format = "%d %b<br>%H:%M:%S" if cross_date else "%H:%M:%S"
        tick_labels = [instants[index].strftime(tick_format) for index in tick_indices]
    figure = go.Figure(go.Scatter(
        x=[row["timestamp"] for row in rows], y=[row["packets"] for row in rows],
        customdata=[[row["bytes"]] for row in rows],
        mode="lines+markers" if len(rows) == 1 else "lines",
        line={"color": "#359dff", "width": 1.7, "shape": "linear"},
        marker={"color": "#359dff", "size": 5},
        fill="tozeroy", fillcolor="rgba(37,140,255,.10)",
        hovertemplate="%{x|%Y-%m-%d %H:%M:%S} UTC<br>%{y:,} packets<br>%{customdata[0]:,} bytes<extra></extra>",
    ))
    figure.update_layout(
        height=180, margin={"l": 36, "r": 21, "t": 8, "b": 44 if cross_date else 36},
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT, "color": "#92a3ba", "size": 10},
        xaxis={"type": "date", "tickmode": "array", "tickvals": [rows[index]["timestamp"] for index in tick_indices], "ticktext": tick_labels, "tickangle": 0, "automargin": True, "showgrid": False, "zeroline": False, "title": {"text": "UTC", "standoff": 5, "font": {"size": 10}}},
        yaxis={"gridcolor": "rgba(174,195,224,.08)", "zeroline": False, "rangemode": "tozero", "nticks": 4, "automargin": True},
        hoverlabel={"bgcolor": "#1a293e", "font_size": 12},
    )
    st.plotly_chart(figure, theme=None, config={"displayModeBar": False, "scrollZoom": False}, width="stretch")
